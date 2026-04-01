(function() {
    alert("AGI Sentinel Active!"); // अगर यह मैसेज आया, मतलब प्लगइन चल गया
    document.body.style.border = "10px solid #00ffcc";
    document.body.style.marginLeft = "60px";
    
    const guard = document.createElement('div');
    guard.style = "position:fixed; top:0; left:0; width:50px; height:100%; background:black; border-right:2px solid #00ffcc; z-index:9999999; display:flex; align-items:center; justify-content:center; font-size:40px;";
    guard.innerHTML = "🔱";
    document.documentElement.appendChild(guard);
})();
