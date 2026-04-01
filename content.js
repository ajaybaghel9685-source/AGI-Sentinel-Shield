// AGI-SENTINEL-ULTRA: THE HELMET ARMOR EDITION
(function() {
    // 1. HELMET ARMOR ENGINE (Favicon change karne ke liye)
    function applyHelmetArmor() {
        // Purane favicon ko dhoondo
        let link = document.querySelector("link[rel~='icon']");
        if (!link) {
            link = document.createElement('link');
            link.rel = 'icon';
            document.getElementsByTagName('head')[0].appendChild(link);
        }

        // Helmet Icon ka Canvas base (Ye website ke icon ke upar shield banayega)
        const canvas = document.createElement('canvas');
        canvas.width = 32;
        canvas.height = 32;
        const ctx = canvas.getContext('2d');

        const img = new Image();
        img.crossOrigin = "anonymous";
        img.src = link.href;

        img.onload = function() {
            // Asli logo draw karo
            ctx.drawImage(img, 0, 0, 32, 32);
            
            // Uske upar "AGI HELMET" (Blue/Green Shield Overlay)
            ctx.strokeStyle = "#00ffcc";
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.arc(16, 16, 14, 0, Math.PI * 2); // Bahari Kawach
            ctx.stroke();
            
            // Ek chota chamakta hua dot (Active Signal)
            ctx.fillStyle = "#00ffcc";
            ctx.beginPath();
            ctx.arc(26, 6, 4, 0, Math.PI * 2);
            ctx.fill();

            link.href = canvas.toDataURL("image/x-icon");
        };
    }

    // 2. DIVINE ANIMATED GUARDS (Trishul & Snake)
    const styleSheet = document.createElement('style');
    styleSheet.innerHTML = `
        @keyframes snakeMove { 0% { background-position: 0 0; } 100% { background-position: 0 1000px; } }
        @keyframes glowTrishul { 0%, 100% { filter: drop-shadow(0 0 5px #00ffcc); transform: scale(1); } 50% { filter: drop-shadow(0 0 15px #00ffcc); transform: scale(1.1); } }
        .sentinel-guard {
            position: fixed; top: 0; height: 100%; width: 50px; 
            background: #000; z-index: 999999; display: flex; 
            flex-direction: column; align-items: center; justify-content: space-around;
            border-left: 2px solid #00ffcc; border-right: 2px solid #00ffcc;
            animation: snakeMove 15s linear infinite;
            background-image: repeating-linear-gradient(45deg, #001a14 0, #001a14 10px, #000 10px, #000 20px);
        }
        .trishul { animation: glowTrishul 2s infinite; fill: #00ffcc; width: 35px; }
        body { margin: 0 60px !important; background: #000 !important; color: #00ffcc !important; }
    `;
    document.head.appendChild(styleSheet);

    const trishulIcon = `<svg class="trishul" viewbox="0 0 24 24"><path d="M12 2l1.5 4h-3L12 2zm0 20v-9m-4-2c0-3 4-5 4-5s4 2 4 5m-8 0h8M8 11c0 2 2 3 2 3m4-3c0 2-2 3-2 3"/></svg>`;
    
    const leftG = document.createElement('div'); leftG.className = 'sentinel-guard'; leftG.style.left = '0';
    const rightG = document.createElement('div'); rightG.className = 'sentinel-guard'; rightG.style.right = '0';
    leftG.innerHTML = rightG.innerHTML = `<span>🐍</span>${trishulIcon}${trishulIcon}<span>🐍</span>`;
    
    document.documentElement.appendChild(leftG);
    document.documentElement.appendChild(rightG);

    // 3. VOICE & ACTIVATION
    function speak(txt) {
        const s = new SpeechSynthesisUtterance(txt);
        s.lang = 'hi-IN'; s.rate = 0.8;
        window.speechSynthesis.speak(s);
    }

    // Website khulte hi Helmet Armor aur Voice active karein
    applyHelmetArmor();
    speak("एजीआई हेलमेट कवच सक्रिय है। आपकी वेबसाइट अब पूरी तरह सुरक्षित है।");

    // Scanning Overlay
    const ov = document.createElement('div');
    ov.style = "position:fixed;top:0;left:0;width:100%;height:100%;background:#000;color:#00ffcc;z-index:1000001;display:flex;align-items:center;justify-content:center;font-family:monospace;";
    ov.innerHTML = "<h1>[ ARMORING INTERFACE... ]</h1>";
    document.documentElement.appendChild(ov);

    setTimeout(() => {
        ov.style.opacity = '0';
        setTimeout(() => ov.remove(), 1000);
    }, 2000);
})();
