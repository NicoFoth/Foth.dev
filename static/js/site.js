/* foth.dev -- no framework, no build step. Read along, it's short. */
(() => {
  'use strict';

  const body = document.body;
  const csrf = document.querySelector('meta[name="csrf-token"]')?.content || '';
  const order = (body.dataset.starOrder || '').split(',').filter(Boolean);
  const have = new Set((body.dataset.stars || '').split(',').filter(Boolean));

  const store = {
    get(key) { try { return localStorage.getItem(key); } catch { return null; } },
    set(key, value) { try { localStorage.setItem(key, value); } catch { /* private mode */ } },
  };

  /* ------------------------------------------------------------- stars */

  function toast(text) {
    const el = document.createElement('div');
    el.className = 'toast';
    el.setAttribute('role', 'status');
    el.textContent = text;
    body.appendChild(el);
    setTimeout(() => el.remove(), 5200);
  }

  function lightSlot(key) {
    const slot = document.querySelector(`[data-slot="${order.indexOf(key)}"]`);
    if (slot) slot.className = 'sc-O';
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

  // The server already recorded the star; just tell the visitor.
  function celebrate(key, title) {
    have.add(key);
    document.querySelectorAll('[data-star-count]').forEach((el) => { el.textContent = have.size; });
    lightSlot(key);
    toast(`You found a star: ${title}! [${have.size}/${order.length}]`);
  }

  /* ------------------------------------------------------------ uptime */

  const uptime = document.querySelector('[data-uptime]');
  if (uptime) {
    const born = new Date(uptime.dataset.uptime).getTime();
    const year = 365.2425 * 24 * 3600 * 1000;
    const tick = () => { uptime.textContent = ((Date.now() - born) / year).toFixed(9); };
    tick();
    setInterval(tick, 50);
  }

  /* --------------------------------------------------------- night owl */

  const hour = new Date().getHours();
  if (hour < 5 && !have.has('owl')) claim('owl');

  /* -------------------------------------------------------------- moon */

  let moonClicks = 0;
  document.addEventListener('click', (event) => {
    const moon = event.target.closest('.moon');
    if (!moon) return;
    event.preventDefault();
    moonClicks += 1;
    document.querySelectorAll('.moon').forEach((el) => {
      el.style.textShadow = `0 0 ${4 + moonClicks * 4}px #ffff99`;
    });
    if (moonClicks === 3) claim('moon');
  });

  /* ------------------------------------------------------------ konami */

  const KONAMI = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
  let konamiAt = 0;

  function starfall() {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    for (let i = 0; i < 40; i++) {
      const star = document.createElement('span');
      star.className = 'falling-star';
      star.textContent = '*';
      star.style.left = `${Math.random() * 100}vw`;
      star.style.animationDuration = `${1.5 + Math.random() * 2.5}s`;
      star.style.animationDelay = `${Math.random() * 1.5}s`;
      body.appendChild(star);
      setTimeout(() => star.remove(), 6000);
    }
  }

  function konami(key) {
    konamiAt = key === KONAMI[konamiAt] ? konamiAt + 1 : (key === KONAMI[0] ? 1 : 0);
    if (konamiAt === KONAMI.length) {
      konamiAt = 0;
      starfall();
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
    '~': '/', home: '/', about: '/about/', projects: '/projects/', puzzle: '/puzzle/',
    stars: '/stars/', contact: '/contact/', cs: '/cs/', poker: '/poker/', legal: '/legal/',
  };
  const FILES = {
    'readme.txt': () => [
      'foth.dev',
      '========',
      'A personal site, built like a terminal and lit like Advent of Code.',
      '',
      'There are ' + order.length + ' stars hidden around here. `stars` shows your progress.',
      'Pages are directories. `ls` lists them, `cd` goes there.',
    ],
    'todo.txt': () => [
      '[x] rewrite the website',
      '[x] hide some stars',
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
        '  stars              show your star count',
        '  unlock <code>      redeem a code found elsewhere',
        '  whoami, pwd, date, uptime, echo, history, clear',
        '  contrast           toggle high-contrast mode',
        '  exit               close the terminal (or press Esc)',
        '',
        'Keyboard: `:` opens this terminal, `?` shows this help,',
        '`g` then h/a/p/z/s/c jumps to home/about/projects/puzzle/stars/contact.',
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
        // fetching humans.txt is what earns the star, server side
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
    stars() {
      print(`${have.size}/${order.length} stars found.`, 't-star');
      print('Hints live on /stars/. Type `cd stars` to go there.');
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
      if (result.new) print('...although. Reported to whom? Have a star.', 't-star');
    },
    async unlock(args) {
      if (!args[0]) return print('unlock: missing code. Codes are found outside the browser.', 't-err');
      const result = await claim('curl', { code: args[0] });
      if (!result.ok) return print(`unlock: ${result.error || 'invalid code'}`, 't-err');
      print(result.new ? 'Code accepted.' : 'Already unlocked.', result.new ? 't-star' : 't-ok');
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
      const sha = document.querySelector('.site-footer a[href*="/commit/"]')?.textContent || 'dev';
      if (args[0] === 'log') return lines([`commit ${sha}`, 'Author: Nico Foth', '', '    redesign: make it look like a terminal at night']);
      if (args[0] === 'blame') return print('It was me. It is always me.');
      print('git: try `git log`');
    },
  };
  COMMANDS.open = COMMANDS.cd;
  COMMANDS.dir = COMMANDS.ls;
  COMMANDS.type = COMMANDS.cat;
  COMMANDS.cls = COMMANDS.clear;
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

  function openTerminal(command) {
    term.hidden = false;
    if (!greeted) {
      greeted = true;
      print(`foth.dev shell. ${have.size}/${order.length} stars found. Type \`help\` to get started.`, 'dim');
    }
    input.focus();
    if (command) run(command);
  }

  function closeTerminal() {
    term.hidden = true;
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

  document.querySelectorAll('[data-open-terminal]').forEach((link) => {
    link.addEventListener('click', (event) => { event.preventDefault(); openTerminal(); });
  });
  if (location.hash === '#terminal') openTerminal();

  /* ---------------------------------------------------------- keyboard */

  let pendingG = false;
  const JUMPS = { h: '/', a: '/about/', p: '/projects/', z: '/puzzle/', s: '/stars/', c: '/contact/' };

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !term.hidden) { closeTerminal(); return; }
    const typing = event.target.closest('input, textarea, select, [contenteditable]');
    if (!typing) konami(event.key);
    if (typing || event.ctrlKey || event.metaKey || event.altKey) return;

    if (pendingG) {
      pendingG = false;
      if (JUMPS[event.key]) { location.href = JUMPS[event.key]; return; }
    }
    if (event.key === ':' || event.key === '`') { event.preventDefault(); openTerminal(); }
    else if (event.key === '?') { event.preventDefault(); openTerminal('help'); }
    else if (event.key === 'g') { pendingG = true; setTimeout(() => { pendingG = false; }, 1000); }
  });

  /* ---------------------------------------------------------- contrast */

  if (store.get('hc') === '1') body.classList.add('hc');

  /* ------------------------------------------------- for the curious */

  console.log(
    '%c*%c  Hello, fellow developer.\n   There are ' + order.length + ' stars on this site. Some of them are only reachable from here,\n   or from your own terminal. Press : for a shell.',
    'color:#ffff66;text-shadow:0 0 5px #ffff66;font-size:16px', 'color:#00cc00',
  );
})();
