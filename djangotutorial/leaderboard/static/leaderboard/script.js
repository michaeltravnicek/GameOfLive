window.addEventListener('load', function(){
    document.querySelectorAll('table tr td').forEach((td, i) => {
        td.style.animationDelay = (i * 0.01) + "s";
    });
});

function showSection(sectionId, event) {
    document.querySelectorAll('.container').forEach(function(section) {
        section.classList.add('hidden');
    });
    document.getElementById(sectionId).classList.remove('hidden');

    document.querySelectorAll('.menu-item').forEach(function(item) {
        item.classList.remove('active');
    });
    event.target.classList.add('active');
}

function loadUser(userId) {
    const content = document.getElementById("leaderboard");
    content.classList.add("fade-out");

    setTimeout(() => {
        fetch(`/user/${userId}/`)
            .then(response => response.json())
            .then(data => {
                
                content.innerHTML = `
                    <div class="user-header">
                        <button class="back-button" onclick="loadLeaderboard()">Back</button>
                    </div>
                    <h1 class="center-title">${data.user_name}</h1>
                    <table>
                        <colgroup>
                            <col style="width: auto;">
                            <col style="width: 25%;">
                            <col style="width: 20%;">
                            <col style="width: 10%;">
                        </colgroup>
                        <tr>
                            <th>Akce</th>
                            <th>Lokace</th>
                            <th>Datum</th>
                            <th>Body</th>
                        </tr>
                        ${data.actions.map(action => `
                            <tr>
                                <td>${action.event__name}</td>
                                <td>${action.event__place}</td>
                                <td>${new Date(action.event__date).toLocaleDateString('cs-CZ')}</td>
                                <td>${action.event__points}</td>
                            </tr>
                        `).join('')}
                    </table>
                `;
                content.classList.remove("fade-out");
                content.classList.add("fade-in");
            })
            .catch(err => console.error(err));
    }, 500);
}

function loadLeaderboard() {
    const content = document.getElementById("leaderboard");
    content.classList.add("fade-out");

    setTimeout(() => {
        location.reload(); 
    }, 100);
}

document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("event-modal");
    const modalImage = document.getElementById("modal-image");
    const modalName = document.getElementById("modal-name");
    const modalDescription = document.getElementById("modal-description");
    const modalDate = document.getElementById("modal-date");
    const closeBtn = document.querySelector(".close");

    document.querySelectorAll(".event-card").forEach(card => {
        card.addEventListener("click", function() {
            const img = card.querySelector("img");
            const name = card.querySelector("h2").innerText;
            const description = card.querySelector(".description").innerText;
            const date = card.querySelector(".event-date").innerText;

            if (img) {
                modalImage.src = img.src;
                modalImage.style.display = "block";
            } else {
                modalImage.src = "";
                modalImage.style.display = "none";
            }

            modalName.innerText = name;
            modalDescription.innerText = description;
            modalDate.innerText = date;

            modal.classList.add("show");
        });
    });

    closeBtn.addEventListener("click", function() {
        modal.classList.remove("show");
    });

    window.addEventListener("click", function(event) {
        if (event.target === modal) {
            modal.classList.remove("show");
        }
    });
});
