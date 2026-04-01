// AGI-SENTINEL-ULTRA: THE ULTIMATE DHAMKI MODE
(function() {
    "use strict";

    // 1. VOODOO VOICE (Bhaari aur डरावनी आवाज़)
    function dhumkiVoice(text) {
        window.speechSynthesis.cancel(); 
        const speech = new SpeechSynthesisUtterance(text);
        speech.lang = 'hi-IN';
        speech.rate = 0.7; // एकदम धीमी और डरावनी
        speech.pitch = 0.2; // बहुत भारी आवाज़
        window.speechSynthesis.speak(speech);
    }

    // 2. THE KILL-SWITCH UI (पूरा पेज कब्जा करने के लिए)
    function activateDhamki() {
        document.documentElement.innerHTML = `
            <div style="background:black; color:red; height:100vh; width:100vw; display:flex; flex-direction:column; align-items:center; justify-content:center; font-family:serif; text-align:center; position:fixed; top:0; left:0; z-index:2147483647; overflow:hidden; border:20px double red;">
                <h1 style="font-size:70px; margin:0; text-shadow: 0 0 30px red; animation: blink 0.5s infinite;">⚠️ मौत का घेरा ⚠️</h1>
                <div style="font-size:120px; margin:20px;">🔱</div>
                <h2 style="font-size:40px; color:white;">AGI SENTINEL: तुझे चेतावनी दी थी!</h2>
                <p style="font-size:25px; padding:0 20px;">तेरी रूह कांप जाएगी जब तेरा डेटा मेरे पास होगा।</p>
                <div style="background:red; color:black; font-weight:bold; font-size:30px; padding:10px; width:100%;">तू अब हमारे रडार पर है!</div>
                <p style="font-size:20px; margin-top:30px; color:gray;">(3 सेकंड में तेरा सिस्टम लॉक हो जाएगा...)</p>
                <style>
                    @keyframes blink { 0% {opacity:1;} 50% {opacity:0.2;} 100% {opacity:1;} }
                    body { cursor: none !important; }
                </style>
            </div>
        `;
        
        dhumkiVoice("एजीआई सेंटिनल ने तुझे पकड़ लिया है। अब तेरी खैर नहीं। अपनी मौत को सामने देख, क्योंकि तूने हमारी सीमा पार की है। यहाँ से भाग जा, वरना सब कुछ खत्म कर दूँगा।");
    }

    // 3. AUTO-EXECUTE ON DANGER (URL Check)
    const url = window.location.href.toLowerCase();
    
    // अगर URL में इनमें से कुछ भी मिले, तो सीधा हमला!
    if(url.includes('0') || url.includes('free') || url.includes('hack') || url.includes('sex') || url.includes('porn')) {
        activateDhamki();
    } else {
        // Normal sites के लिए स्वागत
        console.log("AGI Shield Active: Safe Zone.");
    }
})();
