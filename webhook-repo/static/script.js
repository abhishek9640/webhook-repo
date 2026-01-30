document.addEventListener("DOMContentLoaded", function () {
    const eventsContainer = document.getElementById("events-container");

    function fetchEvents() {
        fetch("/events")
            .then(response => response.json())
            .then(data => {
                renderEvents(data);
            })
            .catch(error => console.error("Error fetching events:", error));
    }

    function renderEvents(events) {
        if (events.length === 0) {
            eventsContainer.innerHTML = '<p class="loading">No events found yet.</p>';
            return;
        }

        eventsContainer.innerHTML = ""; // Clear existing content

        events.forEach(event => {
            const card = document.createElement("div");
            card.className = `event-card ${event.action}`;
            
            let message = "";
            // Exact format: {author} [action] {branch} on {timestamp}
            if (event.action === "PUSH") {
                message = `<strong>${event.author}</strong> pushed to <strong>${event.to_branch}</strong> on ${event.timestamp}`;
            } else if (event.action === "PULL_REQUEST") {
                message = `<strong>${event.author}</strong> submitted a pull request from <strong>${event.from_branch}</strong> to <strong>${event.to_branch}</strong> on ${event.timestamp}`;
            } else if (event.action === "MERGE") {
                message = `<strong>${event.author}</strong> merged branch <strong>${event.from_branch}</strong> to <strong>${event.to_branch}</strong> on ${event.timestamp}`;
            }

            card.innerHTML = `<div>${message}</div>`;
            
            eventsContainer.appendChild(card);
        });
    }

    // Initial fetch
    fetchEvents();

    // Poll every 15 seconds
    setInterval(fetchEvents, 15000);
});
