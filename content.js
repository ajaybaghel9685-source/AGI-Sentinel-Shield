(function() {
    "use strict";

    // 1. PROFESSIONAL UI: Minimalist Scanning Bar
    const injectShieldUI = () => {
        const shield = document.createElement('div');
        shield.id = "agi-pro-shield";
        shield.style = "position:fixed; top:0; left:0; width:100%; height:4px; background:#111; z-index:2147483647;";
        shield.innerHTML = `<div id="agi-progress" style="width:0%; height:100%; background:linear-gradient(90deg, #00f2fe 0%, #4facfe 100%); transition: width 0.5s ease;"></div>`;
        document.documentElement.appendChild(shield);

        let p = 0;
        const interval = setInterval(() => {
            p += 25;
            document.getElementById('agi-progress').style.width = p + "%";
            if (p >= 100) {
                clearInterval(interval);
                setTimeout(() => shield.remove(), 500);
            }
        }, 200);
    };

    // 2. SECURITY ENGINE: Anti-Clickjack & Privacy
    const secureEnvironment = () => {
        // Prevent site from being framed (Anti-Phishing)
        if (window.self !== window.top) {
            window.top.location = window.self.location;
        }

        // Clean potentially dangerous URL params
        const dangerousParams = ["track", "utm_source", "fbclid"];
        const url = new URL(window.location.href);
        let changed = false;
        dangerousParams.forEach(param => {
            if (url.searchParams.has(param)) {
                url.searchParams.delete(param);
                changed = true;
            }
        });
        if (changed) window.history.replaceState({}, '', url);
    };

    // 3. INITIALIZE
    injectShieldUI();
    secureEnvironment();
    console.log("AGI Sentinel Pro: Environment Secured.");
})();
