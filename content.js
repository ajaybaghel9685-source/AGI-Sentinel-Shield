const SHIELD_KEY = "AGI_ULTRA_2026";

(async function() {
    const loader = document.createElement('div');
    loader.id = 'ultra-shield-loader';
    loader.innerHTML = `
        <div style="position:fixed;top:0;left:0;width:100%;height:100%;background:radial-gradient(circle,#0a0e17,#010204);z-index:9999999;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#00f2fe;font-family:sans-serif;">
            <div style="width:50px;height:50px;border:3px solid #00f2fe;border-top:3px solid transparent;border-radius:50%;animation:spin 0.6s linear infinite;"></div>
            <h2 style="margin-top:20px;letter-spacing:3px;font-weight:800;">AGI SENTINEL ULTRA</h2>
            <p style="opacity:0.6;font-size:12px;">SECURE LINK VERIFICATION...</p>
        </div>
        <style>@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}</style>
    `;
    document.documentElement.appendChild(loader);

    const params = new URLSearchParams(window.location.search);
    const sig = params.get('sig');

    if (sig) {
        const dataToVerify = window.location.href.split('&sig=')[0] + SHIELD_KEY;
        const msgUint8 = new TextEncoder().encode(dataToVerify);
        const hashBuffer = await crypto.subtle.digest('SHA-256', msgUint8);
        const expectedSig = Array.from(new Uint8Array(hashBuffer)).map(b => b.toString(16).padStart(2, '0')).join('');

        if (sig !== expectedSig) {
            document.documentElement.innerHTML = `
                <div style="background:#000;color:#ff3333;height:100vh;display:flex;align-items:center;justify-content:center;font-family:sans-serif;text-align:center;">
                    <div><h1>❌ ACCESS DENIED</h1><p>Tamper Detected by Ultra Shield.</p></div>
                </div>`;
            return;
        }
    }
    setTimeout(() => { if(loader) loader.remove(); }, 600);
})();
