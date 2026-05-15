/**
 * Vaccine Record Manager - UI Enhancements Script (Reliable Parent-Targeted Version)
 */

(function() {
    // 1. Get the parent document (where the app actually lives)
    const parentDoc = window.parent.document;

    const runAnimations = () => {
        // --- Digital CountUp ---
        const numbers = parentDoc.querySelectorAll('.stat-number');
        numbers.forEach(el => {
            if (el.dataset.counted === "true") return;
            const target = parseInt(el.innerText);
            if (isNaN(target)) return;
            
            el.dataset.counted = "true";
            let start = 0;
            const duration = 1000;
            const startTime = performance.now();
            
            const animate = (time) => {
                const elapsed = time - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 4);
                el.innerText = Math.floor(eased * target);
                if (progress < 1) requestAnimationFrame(animate);
                else el.innerText = target;
            };
            requestAnimationFrame(animate);
        });
    };

    // --- High-Performance 3D Tilt using Event Delegation ---
    // Instead of binding to each card, we listen on the whole document
    parentDoc.addEventListener('mousemove', (e) => {
        const card = e.target.closest('.stat-card');
        if (!card) return;

        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        // Tilt more aggressively (up to 15 degrees)
        const rotateX = ((centerY - y) / centerY) * 15;
        const rotateY = ((x - centerX) / centerX) * 15;
        
        card.style.transition = "transform 0.1s ease-out";
        card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.05, 1.05, 1.05) translateY(-5px)`;
        card.style.zIndex = "100";
        card.style.boxShadow = "0 30px 60px -12px rgba(0,0,0,0.15)";
    });

    // Reset when mouse leaves the card
    parentDoc.addEventListener('mouseout', (e) => {
        const card = e.target.closest('.stat-card');
        if (!card) return;
        
        // Only reset if we are actually leaving the card container
        const related = e.relatedTarget;
        if (!related || !card.contains(related)) {
            card.style.transition = "transform 0.5s ease";
            card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1) translateY(0)";
            card.style.zIndex = "1";
            card.style.boxShadow = "0 1px 2px rgba(0,0,0,0.05)";
        }
    });

    // --- Ripple Effect Delegation ---
    parentDoc.addEventListener('mousedown', (e) => {
        const btn = e.target.closest('.stButton > button');
        if (!btn) return;

        const rect = btn.getBoundingClientRect();
        const circle = parentDoc.createElement("span");
        const diameter = Math.max(btn.clientWidth, btn.clientHeight);
        
        circle.style.width = circle.style.height = `${diameter}px`;
        circle.style.left = `${e.clientX - rect.left - diameter/2}px`;
        circle.style.top = `${e.clientY - rect.top - diameter/2}px`;
        circle.className = "ripple";
        
        btn.appendChild(circle);
        setTimeout(() => circle.remove(), 600);
    });

    // Periodically check for new numbers to animate (Streamlit is dynamic)
    setInterval(runAnimations, 1000);
    runAnimations();

})();
