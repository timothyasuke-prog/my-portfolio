// Main UI interactions: theme toggle, marquee control, small UI glows
(function(){
	const themeToggle = document.getElementById('themeToggle');
	const body = document.body;

	function applyTheme(name) {
		if (name === 'dark') {
			body.classList.add('dark-mode');
			if (themeToggle) themeToggle.textContent = '🌙';
		} else {
			body.classList.remove('dark-mode');
			if (themeToggle) themeToggle.textContent = '🌗';
		}
	}

	// initialize from localStorage or prefers-color-scheme
	const stored = localStorage.getItem('site-theme');
	if (stored) applyTheme(stored);
	else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) applyTheme('dark');

	if (themeToggle) {
		themeToggle.addEventListener('click', () => {
			const isDark = body.classList.toggle('dark-mode');
			localStorage.setItem('site-theme', isDark ? 'dark' : 'light');
			applyTheme(isDark ? 'dark' : 'light');
		});
	}

	// Add a decorative glow layer in hero if missing
	window.addEventListener('load', () => {
		const hero = document.querySelector('.hero');
		if (hero && !hero.querySelector('.glow-anim')) {
			const glow = document.createElement('div');
			glow.className = 'glow-anim';
			hero.prepend(glow);
		}

		// ensure marquee duplicates enough items for smooth loop
		document.querySelectorAll('.marquee-track').forEach(track => {
			// if track width less than parent, duplicate once
			const parent = track.parentElement;
			if (track.scrollWidth < parent.offsetWidth * 2) {
				const clone = track.innerHTML;
				track.innerHTML += clone;
			}
		});
	});



// Starfield + background hearts generator
(function starfieldModule(){
    function rand(min, max){ return Math.random() * (max - min) + min; }

    const container = document.createElement('div');
    container.className = 'starfield';
    document.documentElement.appendChild(container);

    const w = () => Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
    const h = () => Math.max(document.documentElement.clientHeight, window.innerHeight || 0);

    function makeStar(i){
        const s = document.createElement('div');
        s.className = 'star';
        const sizeType = Math.random();
        if (sizeType > 0.85) s.classList.add('big');
        else if (sizeType > 0.5) s.classList.add('med');
        else s.classList.add('small');

        // color variations
        const c = Math.random();
        if (c > 0.66) s.classList.add('accent1');
        else if (c > 0.33) s.classList.add('accent2');
        else s.classList.add('accent3');

        const left = rand(0, w());
        const top = rand(0, h());
        s.style.left = left + 'px';
        s.style.top = top + 'px';

        const dur = rand(3, 9).toFixed(2) + 's';
        s.style.animation = 'twinkle ' + dur + ' linear ' + rand(0, 3).toFixed(2) + 's infinite';

        container.appendChild(s);
    }

    function makeHearts(count){
        for (let i=0;i<count;i++){
            const heart = document.createElement('div');
            heart.className = 'bg-heart';
            const left = rand(0, w());
            const start = rand(h()*0.6, h());
            heart.style.left = left + 'px';
            heart.style.top = start + 'px';
            const dur = rand(10, 28).toFixed(2) + 's';
            heart.style.animation = 'floatUp ' + dur + ' linear ' + rand(0,5).toFixed(2) + 's forwards';
            heart.style.opacity = 0.9;
            container.appendChild(heart);
        }
    }

    function populate(){
        container.innerHTML = '';
        const stars = Math.round((w() * h()) / 45000); // density
        for (let i=0;i<stars;i++) makeStar(i);
        // a few hearts for lovey effect
        makeHearts(6);
    }

    window.addEventListener('resize', () => {
        // throttle small windows
        clearTimeout(window._starResize);
        window._starResize = setTimeout(populate, 300);
    });

    // Wait until DOM loaded and then populate
    if (document.readyState === 'complete' || document.readyState === 'interactive') populate();
    else document.addEventListener('DOMContentLoaded', populate);

})();

})
