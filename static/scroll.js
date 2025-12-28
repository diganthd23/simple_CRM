document.addEventListener("DOMContentLoaded", () => {
    const elements = document.querySelectorAll(
        ".reveal-up, .reveal-left, .reveal-right"
    );

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("reveal-active");
                }
            });
        },
        { threshold: 0.2 }
    );

    elements.forEach((el) => observer.observe(el));
});
