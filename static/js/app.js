// Auto-dismiss flash toasts after 4 seconds
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.toast').forEach((toast, i) => {
        setTimeout(() => {
            toast.style.transition = 'opacity .4s, transform .4s';
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(30px)';
            setTimeout(() => toast.remove(), 400);
        }, 4000 + i * 300);
    });

    // Client-side numeric validation feedback
    document.querySelectorAll('input[type=number]').forEach(inp => {
        inp.addEventListener('input', () => {
            const min = parseFloat(inp.min);
            const max = parseFloat(inp.max);
            const val = parseFloat(inp.value);
            if (!isNaN(val) && ((!isNaN(min) && val < min) || (!isNaN(max) && val > max))) {
                inp.style.borderColor = '#ef4444';
            } else {
                inp.style.borderColor = '';
            }
        });
    });
});