// static/js/main.js

// Confirm delete action
document.addEventListener("DOMContentLoaded", function () {
  const deleteLinks = document.querySelectorAll("a.btn.danger");
  deleteLinks.forEach(link => {
    link.addEventListener("click", function (e) {
      if (!confirm("Are you sure you want to delete this job?")) {
        e.preventDefault();
      }
    });
  });
});

// Auto-hide flash messages after 4 seconds
document.addEventListener("DOMContentLoaded", function () {
  const flashes = document.querySelectorAll(".flash");
  if (flashes.length > 0) {
    setTimeout(() => {
      flashes.forEach(flash => {
        flash.style.transition = "opacity 0.5s";
        flash.style.opacity = 0;
        setTimeout(() => flash.remove(), 500);
      });
    }, 4000);
  }
});

// Optional: Instant job search (AJAX preview)
const searchForm = document.querySelector("form[action='/jobs']");
if (searchForm) {
  searchForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    const query = this.querySelector("input[name='q']").value;
    const res = await fetch(`/jobs?q=${encodeURIComponent(query)}`);
    const html = await res.text();

    // Replace job list dynamically
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, "text/html");
    const newList = doc.querySelector(".job-list");
    document.querySelector(".job-list").innerHTML = newList.innerHTML;
  });
}
