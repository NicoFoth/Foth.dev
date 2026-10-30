/* foth.dev, plain JavaScript without a framework or a build step. Read along, it's short. */
(() => {
  'use strict';

  const body = document.body;
  const csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';
  const order = (body.dataset.bitOrder || '').split(',').filter(Boolean);
  const have = new Set((body.dataset.bits || '').split(',').filter(Boolean));
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');

  const store = {
    get(key) { try { return localStorage.getItem(key); } catch { return null; } },
    set(key, value) { try { localStorage.setItem(key, value); } catch { /* private mode */ } },
  };

  /* ---------------------------------------------------- colour schemes */

  // t then 1-4. The colours live in site.css; base.html applies the saved one before the first paint.
  const THEMES = ['phosphor', 'amber', 'midnight', 'darkroom'];
  const DEFAULT_THEME = 'darkroom';
  const themeMeta = document.querySelector('meta[name="theme-color"]');
  const currentTheme = () => document.documentElement.dataset.theme || DEFAULT_THEME;

  function setTheme(name) {
    if (name === DEFAULT_THEME) delete document.documentElement.dataset.theme;
    else document.documentElement.dataset.theme = name;
    store.set('theme', name === DEFAULT_THEME ? '' : name);
    themeMeta?.setAttribute('content', getComputedStyle(document.documentElement).getPropertyValue('--bg').trim());
  }
  setTheme(currentTheme());

  /* -------------------------------------------------------------- bits */

  // Twelve bits make a register. The status line shows it as LEDs, bit 0 on the right.
  const toasts = document.querySelector('.toasts');

  function toast(text) {
    const el = document.createElement('p');
    el.className = 'toast';
    el.textContent = text;
    toasts.appendChild(el);
    setTimeout(() => el.remove(), 5600);
  }

  function setLed(key) {
    const led = document.querySelector(`.leds [data-bit="${key}"]`);
    if (!led) return;
    led.classList.add('on', 'just-on');
    led.addEventListener('animationend', () => led.classList.remove('just-on'), { once: true });
  }

  async function claim(key, extra = {}) {
    if (have.has(key) && key !== 'curl') return { ok: true, new: false };
    let data;
    try {
      const response = await fetch(body.dataset.claimUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
        body: JSON.stringify({ key, ...extra }),
        credentials: 'same-origin',
      });
      data = await response.json();
    } catch {
      return { ok: false, error: 'network error' };
    }
    if (data.ok && data.new) celebrate(key, data.title);
    return data;
  }

  // The server already recorded the bit; just tell the visitor.
  function celebrate(key, title) {
    have.add(key);
    document.querySelectorAll('[data-bit-count]').forEach((el) => { el.textContent = have.size; });
    document.querySelector('.register')?.setAttribute('aria-label', `${have.size} of ${order.length} bits found`);
    setLed(key);
    toast(`Bit set: ${title}. ${have.size} of ${order.length} found.`);
  }

  /* ------------------------------------------------------------ uptime */

  const uptime = document.querySelector('[data-uptime]');
  if (uptime) {
    const born = new Date(uptime.dataset.uptime).getTime();
    const year = 365.2425 * 24 * 3600 * 1000;
    const tick = () => { uptime.textContent = ((Date.now() - born) / year).toFixed(reduceMotion.matches ? 4 : 9); };
    tick();
    setInterval(tick, reduceMotion.matches ? 60000 : 50);
  }

  /* -------------------------------------------------------- tmux clock */

  // tmux shows the time on the right of its status line; this one shows the visitor's
  const clock = document.querySelector('[data-clock]');
  if (clock) {
    const pad = (n) => String(n).padStart(2, '0');
    const show = () => {
      const now = new Date();
      clock.textContent = `${pad(now.getHours())}:${pad(now.getMinutes())} ${pad(now.getDate())}-${now.toLocaleString('en', { month: 'short' })}-${String(now.getFullYear()).slice(2)}`;
      clock.dateTime = now.toISOString();
    };
    show();
    clock.hidden = false;
    setInterval(show, 10000);
  }

  /* --------------------------------------------------------- night owl */

  const hour = new Date().getHours();
  if (hour < 5 && !have.has('owl')) claim('owl');

  /* ------------------------------------------------------- loose LED */

  // One LED on the front page panel flickers. Tap it three times and it holds.
  const loose = document.querySelector('[data-loose]');
  if (loose) {
    let taps = 0;
    const tap = () => {
      if (loose.classList.contains('fixed')) return;
      taps += 1;
      loose.classList.remove('jolt');
      void loose.getBoundingClientRect();  // restart the jolt animation
      loose.classList.add('jolt');
      if (taps < 3) return;
      loose.classList.add('fixed');
      loose.setAttribute('aria-label', 'Repaired LED');
      claim('flicker');
    };
    loose.addEventListener('click', tap);
    loose.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); tap(); }
    });
  }

  /* ------------------------------------------------------------ konami */

  const KONAMI = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
  let konamiAt = 0;

  function bitRain() {
    if (reduceMotion.matches) return;
    for (let i = 0; i < 48; i++) {
      const bit = document.createElement('span');
      bit.className = 'rain';
      bit.setAttribute('aria-hidden', 'true');
      bit.textContent = Math.random() < .5 ? '0' : '1';
      bit.style.left = `${Math.random() * 100}vw`;
      bit.style.animationDuration = `${1.5 + Math.random() * 2.5}s`;
      bit.style.animationDelay = `${Math.random() * 1.5}s`;
      body.appendChild(bit);
      setTimeout(() => bit.remove(), 6000);
    }
  }

  function konami(key) {
    konamiAt = key === KONAMI[konamiAt] ? konamiAt + 1 : (key === KONAMI[0] ? 1 : 0);
    if (konamiAt === KONAMI.length) {
      konamiAt = 0;
      bitRain();
      claim('konami');
    }
  }

  /* ---------------------------------------------------------- terminal */

  const term = document.getElementById('terminal');
  const out = term.querySelector('.terminal-out');
  const input = term.querySelector('.terminal-input');
  const cmdHistory = [];
  let historyAt = 0;
  let vim = false;
  let greeted = false;

  const PAGES = {
    '~': '/', home: '/', about: '/about/', projects: '/projects/', teaser: '/teaser/',
    bits: '/bits/', contact: '/contact/', cs: '/cs/', poker: '/poker/', legal: '/legal/',
  };
  const FILES = {
    'readme.txt': () => [
      'foth.dev',
      '========',
      "Nico Foth's personal website.",
      '',
      order.length + ' bits are hidden around here. `bits` shows your register.',
      'Pages are directories. `ls` lists them, `cd` goes there.',
    ],
    'todo.txt': () => [
      '[x] rewrite the website',
      '[x] hide some bits',
      '[ ] write more blog posts (there is no blog)',
      '[ ] sleep',
    ],
    'robots.txt': 'fetch',
    'humans.txt': 'fetch',
  };

  function print(text = '', cls = '') {
    const line = document.createElement('div');
    if (cls) line.className = cls;
    line.textContent = text;
    out.appendChild(line);
    out.scrollTop = out.scrollHeight;
    return line;
  }
  const lines = (list, cls) => list.forEach((text) => print(text, cls));

  function go(path) {
    print(`cd ${path}`, 't-ok');
    setTimeout(() => { location.href = path; }, 150);
  }

  function resolvePage(arg) {
    const name = (arg || '~').replace(/^(\.\/|\/|~\/)/, '').replace(/\/$/, '') || '~';
    if (name === '..') return '/';
    return PAGES[name];
  }

  const COMMANDS = {
    help() {
      lines([
        'Available commands:',
        '  ls                 list pages and files',
        '  cd <page>          go to a page (also: open)',
        '  cat <file>         print a file',
        '  bits               show which bits are set',
        '  unlock <code>      redeem a code found elsewhere',
        '  whoami, pwd, date, uptime, echo, history, clear',
        '  theme [name|1-4]   list or switch colour schemes',
        '  contrast           toggle high-contrast mode',
        '  exit               close the terminal (or press Esc)',
        '',
        'Keyboard: `:` opens this terminal, `?` shows this help,',
        '`g` then 1-7 switches window, as in the bar at the top;',
        '`g` then h/a/p/t/b/c jumps to home/about/projects/teaser/bits/contact;',
        '`t` then 1-4 switches colours: phosphor, amber, midnight, darkroom.',
      ]);
    },
    ls(args) {
      if (args[0] === '-a' || args[0] === '-la' || args[0] === '-al') print('.  ..  .secrets/', 'dim');
      print(Object.keys(PAGES).filter((p) => p !== '~' && p !== 'home').map((p) => p + '/').join('  '));
      print(Object.keys(FILES).join('  '));
    },
    cd(args) {
      if (args[0] === '.secrets' || args[0] === '.secrets/') return print('cd: .secrets: Permission denied', 't-err');
      const path = resolvePage(args[0]);
      if (!path) return print(`cd: ${args[0]}: No such file or directory`, 't-err');
      go(path);
    },
    async cat(args) {
      if (!args.length) return print('cat: missing operand. Usage: cat <file>', 't-err');
      const file = FILES[args[0]];
      if (!file) {
        if (resolvePage(args[0])) return print(`cat: ${args[0]}: Is a directory`, 't-err');
        return print(`cat: ${args[0]}: No such file or directory`, 't-err');
      }
      if (file !== 'fetch') return lines(file());
      try {
        const response = await fetch('/' + args[0], { credentials: 'same-origin' });
        lines((await response.text()).trimEnd().split('\n'));
        // fetching humans.txt is what sets the bit, server side
        if (args[0] === 'humans.txt' && !have.has('humans')) celebrate('humans', 'Credits');
      } catch {
        print(`cat: ${args[0]}: Network is unreachable`, 't-err');
      }
    },
    whoami: () => print('visitor'),
    pwd: () => print('/home/visitor' + location.pathname.replace(/\/$/, '')),
    date: () => print(new Date().toString()),
    uptime: () => print(`up ${document.querySelector('[data-uptime]')?.textContent || '?'} years, 1 user, load average: 0.42, 0.13, 0.37`),
    echo: (args) => print(args.join(' ')),
    history: () => cmdHistory.forEach((cmd, i) => print(`${String(i + 1).padStart(4)}  ${cmd}`)),
    clear: () => { out.textContent = ''; },
    exit: () => closeTerminal(),
    bits() {
      const value = order.reduce((sum, key, i) => sum + (have.has(key) ? 2 ** i : 0), 0);
      const binary = value.toString(2).padStart(order.length, '0').replace(/(....)(?=.)/g, '$1 ');
      print(`0x${value.toString(16).toUpperCase().padStart(3, '0')}  ${binary}`, 't-bit');
      print(`${have.size} of ${order.length} bits set. Hints are on /bits/, \`cd bits\` goes there.`);
    },
    theme(args) {
      const arg = (args[0] || '').toLowerCase();
      const name = THEMES[Number(arg) - 1] || (THEMES.includes(arg) ? arg : null);
      if (!arg) {
        THEMES.forEach((theme, i) => print(`${theme === currentTheme() ? '*' : ' '} ${i + 1}  ${theme}`));
        return print('Usage: theme <name|1-4>, or press t then 1-4.', 'dim');
      }
      if (!name) return print(`theme: ${args[0]}: no such colour scheme. Try \`theme\`.`, 't-err');
      setTheme(name);
      print(`colours: ${name}`, 't-ok');
    },
    contrast() {
      const on = body.classList.toggle('hc');
      store.set('hc', on ? '1' : '');
      print(`high contrast ${on ? 'on' : 'off'}`, 't-ok');
    },
    async sudo(args) {
      if (args.join(' ') === 'make me a sandwich') print('Okay.', 't-ok');
      else print('visitor is not in the sudoers file. This incident will be reported.', 't-err');
      const result = await claim('sudo');
      if (result.new) print('...although. Reported to whom? Have a bit instead.', 't-bit');
    },
    async unlock(args) {
      if (!args[0]) return print('unlock: missing code. Codes are found outside the browser.', 't-err');
      const result = await claim('curl', { code: args[0] });
      if (!result.ok) return print(`unlock: ${result.error || 'invalid code'}`, 't-err');
      print(result.new ? 'Code accepted.' : 'Already unlocked.', result.new ? 't-bit' : 't-ok');
    },
    make(args) {
      const what = args.join(' ');
      if (what === 'me a sandwich') return print('What? Make it yourself.', 't-err');
      if (what === 'coffee') return COMMANDS.coffee();
      if (what === 'love') return print("make: *** No rule to make target 'love'. Not war either.", 't-err');
      print('make: *** No targets specified and no makefile found.  Stop.', 't-err');
    },
    coffee() {
      print('Brewing...');
      setTimeout(() => go('/coffee/'), 600);
    },
    rm(args) {
      if (args.includes('-rf') || args.includes('-fr')) return print("Nice try. This server's filesystem is someone else's.", 't-err');
      print(`rm: cannot remove '${args.at(-1) || ''}': Read-only file system`, 't-err');
    },
    vim() {
      vim = true;
      lines(['~', '~', '~                 VIM - Vi IMproved', '~', '~    type  :q<Enter>  to exit', '~'], 'dim');
    },
    curl: () => print("Not from in here. Try it from your real terminal: curl " + location.host, 't-ok'),
    ssh: () => print('ssh: connect to host foth.dev port 22: Connection refused. Good.', 't-err'),
    git(args) {
      const sha = document.querySelector('.footer a[href*="/commit/"]')?.textContent || 'dev';
      if (args[0] === 'log') return lines([`commit ${sha}`, 'Author: Nico Foth', '', '    redesign: lay every page out like a man page']);
      if (args[0] === 'blame') return print('It was me. It is always me.');
      print('git: try `git log`');
    },
  };
  COMMANDS.open = COMMANDS.cd;
  COMMANDS.dir = COMMANDS.ls;
  COMMANDS.type = COMMANDS.cat;
  COMMANDS.cls = COMMANDS.clear;
  COMMANDS.colors = COMMANDS.colours = COMMANDS.theme;
  COMMANDS.brew = COMMANDS.coffee;
  COMMANDS.vi = COMMANDS.nano = COMMANDS.emacs = COMMANDS.vim;
  COMMANDS.quit = COMMANDS.logout = COMMANDS.exit;
  COMMANDS['?'] = COMMANDS.help;

  async function run(raw) {
    const line = raw.trim();
    print(`visitor@foth.dev:~$ ${raw}`, 't-cmd');
    if (!line) return;
    cmdHistory.push(line);
    historyAt = cmdHistory.length;

    if (vim) {
      if ([':q', ':q!', ':wq', ':x', 'ZZ'].includes(line)) { vim = false; return print('Exited vim. Put that on your CV.', 't-ok'); }
      return print(`E492: Not an editor command: ${line.replace(/^:/, '')}`, 't-err');
    }
    if (line === ':q' || line === ':wq') return print("You're not in vim. Yet.");

    const [cmd, ...args] = line.split(/\s+/);
    const fn = COMMANDS[cmd.toLowerCase()];
    if (!fn) return print(`${cmd}: command not found. Try \`help\`.`, 't-err');
    await fn(args);
  }

  function complete() {
    const value = input.value;
    const parts = value.split(/\s+/);
    let pool;
    if (parts.length === 1) pool = Object.keys(COMMANDS);
    else if (/^(cd|open)$/.test(parts[0])) pool = Object.keys(PAGES).filter((p) => p !== '~').map((p) => p + '/');
    else if (/^(cat|type)$/.test(parts[0])) pool = Object.keys(FILES);
    else return;
    const word = parts.at(-1);
    const matches = pool.filter((option) => option.startsWith(word));
    if (matches.length === 1) {
      parts[parts.length - 1] = matches[0] + (parts.length === 1 ? ' ' : '');
      input.value = parts.join(' ');
    } else if (matches.length > 1) {
      print(`visitor@foth.dev:~$ ${value}`, 't-cmd');
      print(matches.join('  '));
    }
  }

  const toggles = document.querySelectorAll('[data-open-terminal]');

  function openTerminal(command) {
    term.hidden = false;
    toggles.forEach((el) => el.setAttribute('aria-expanded', 'true'));
    if (!greeted) {
      greeted = true;
      print(`foth.dev shell. ${have.size} of ${order.length} bits set. Type \`help\` to get started.`, 't-cmd');
    }
    input.focus();
    if (command) run(command);
  }

  function closeTerminal() {
    term.hidden = true;
    toggles.forEach((el) => el.setAttribute('aria-expanded', 'false'));
    input.blur();
    if (location.hash === '#terminal') history.replaceState(null, '', location.pathname + location.search);
  }

  term.querySelector('form').addEventListener('submit', (event) => {
    event.preventDefault();
    const value = input.value;
    input.value = '';
    run(value);
  });

  input.addEventListener('keydown', (event) => {
    if (event.key === 'Tab') { event.preventDefault(); complete(); }
    else if (event.key === 'ArrowUp' && cmdHistory.length) {
      event.preventDefault();
      historyAt = Math.max(0, historyAt - 1);
      input.value = cmdHistory[historyAt];
    } else if (event.key === 'ArrowDown') {
      event.preventDefault();
      historyAt = Math.min(cmdHistory.length, historyAt + 1);
      input.value = cmdHistory[historyAt] || '';
    } else if (event.key === 'l' && event.ctrlKey) { event.preventDefault(); COMMANDS.clear(); }
    else if (event.key === 'c' && event.ctrlKey && !window.getSelection()?.toString()) {
      print(`visitor@foth.dev:~$ ${input.value}^C`, 't-cmd');
      input.value = '';
    }
  });

  out.addEventListener('click', () => { if (!window.getSelection()?.toString()) input.focus(); });

  toggles.forEach((el) => {
    el.addEventListener('click', (event) => {
      event.preventDefault();
      if (term.hidden) openTerminal(); else closeTerminal();
    });
  });
  term.querySelector('[data-close-terminal]').addEventListener('click', closeTerminal);
  if (location.hash === '#terminal') openTerminal();

  /* ---------------------------------------------------------- keyboard */

  // g and t are prefix keys: they wait one second for the key that follows
  let prefix = null;
  let prefixTimer;
  function armPrefix(key) {
    prefix = key;
    clearTimeout(prefixTimer);  // a stale timer from an earlier prefix must not cancel this one
    prefixTimer = setTimeout(() => { prefix = null; }, 1000);
  }
  const JUMPS = { h: '/', a: '/about/', p: '/projects/', t: '/teaser/', b: '/bits/', c: '/contact/' };
  // g then a window number, like tmux's prefix key: the order of the windows in the top bar
  document.querySelectorAll('.windows a').forEach((link, i) => { JUMPS[i + 1] = link.getAttribute('href'); });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !term.hidden) { closeTerminal(); return; }
    const typing = event.target.closest('input, textarea, select, [contenteditable]');
    if (!typing) konami(event.key);
    if (typing || event.ctrlKey || event.metaKey || event.altKey) return;

    const after = prefix;
    prefix = null;
    if (after === 'g' && JUMPS[event.key]) { location.href = JUMPS[event.key]; return; }
    if (after === 't') {
      const theme = THEMES[Number(event.key) - 1];
      if (theme) { setTheme(theme); toast(`Colours: ${theme}. t then 1-4 switches.`); return; }
    }
    if (event.key === ':' || event.key === '`') { event.preventDefault(); openTerminal(); }
    else if (event.key === '?') { event.preventDefault(); openTerminal('help'); }
    else if (event.key === 'g' || event.key === 't') armPrefix(event.key);
  });

  /* ---------------------------------------------------------- contrast */

  if (store.get('hc') === '1') body.classList.add('hc');

  /* ------------------------------------------------- for the curious */

  const css = getComputedStyle(document.documentElement);
  const lit = css.getPropertyValue('--lit').trim();
  console.log(
    '%c●%c  You found the console.\n   There are ' + order.length + ' bits hidden on this site. Some of them are only reachable from here,\n   or from your own terminal. Press : for a shell.',
    `color:${lit};text-shadow:0 0 6px ${lit};font-size:16px`, `color:${css.getPropertyValue('--link').trim()}`,
  );
})();
