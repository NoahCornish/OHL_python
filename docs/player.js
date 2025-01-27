document.addEventListener("DOMContentLoaded", async () => {
    const statsFilePath = "LeagueStats_2024_2025.csv";
    const rostersFilePath = "OHL_ROSTERS_2024_2025.csv";
  
    const teamFilter = document.getElementById("team-filter");
    const playerSearch = document.getElementById("player-search");
    const statsDisplay = document.getElementById("stats-display");
  
    let statsData = [];
    let rosterData = [];
  
    // Load CSV files
    async function loadCSV(filePath) {
      const response = await fetch(filePath);
      const data = await response.text();
      return parseCSV(data);
    }
  
    // Parse CSV into an array of objects
    function parseCSV(data) {
      const rows = data.split("\n").map((row) => row.split(","));
      const headers = rows.shift().map((header) => header.trim());
      return rows
        .filter((row) => row.length === headers.length)
        .map((row) =>
          Object.fromEntries(row.map((value, index) => [headers[index], value.trim()]))
        );
    }
  
    // Populate team filter dropdown
    function populateTeams() {
      const teams = Array.from(new Set(rosterData.map((player) => player["team_name"])));
      teams.sort().forEach((team) => {
        const option = document.createElement("option");
        option.value = team;
        option.textContent = team;
        teamFilter.appendChild(option);
      });
    }
  
    // Filter players by team and search term
    function filterPlayers() {
      const selectedTeam = teamFilter.value;
      const searchQuery = playerSearch.value.toLowerCase();
  
      const filteredPlayers = rosterData.filter((player) => {
        const matchesTeam = selectedTeam === "" || player["team_name"] === selectedTeam;
        const matchesSearch =
          searchQuery === "" ||
          player["full_name"].toLowerCase().includes(searchQuery);
        return matchesTeam && matchesSearch;
      });
  
      displayPlayerList(filteredPlayers);
    }
  
    // Display a list of players matching the filter
    function displayPlayerList(players) {
        if (players.length === 0) {
          statsDisplay.innerHTML = `<p>No players found.</p>`;
          return;
        }
      
        const playerListHTML = players
          .map((player) => {
            const playerId = player["player_id"];
            const playerImage = `https://assets.leaguestat.com/ohl/240x240/${playerId}.jpg`;
            return `
              <div class="player-card">
                <img src="${playerImage}" alt="${player["full_name"]}" class="player-photo" onerror="this.src=''; this.alt='No photo available';">
                <div class="player-info">
                  <p><strong>${player["full_name"]}</strong></p>
                  <p><em>${player["team_name"]}</em></p>
                  <button class="view-stats-btn" data-player="${player["full_name"]}">Get Stats</button>
                </div>
              </div>
            `;
          })
          .join("");
      
        statsDisplay.innerHTML = `<div class="player-list">${playerListHTML}</div>`;
      
        // Add event listeners to all "Get Stats" buttons
        document.querySelectorAll(".view-stats-btn").forEach((button) => {
          button.addEventListener("click", () => {
            const playerName = button.getAttribute("data-player");
            viewPlayerDetails(playerName);
          });
        });
      }
      
  
    // Display detailed stats for a specific player
    // Function to display player stats when "Get Stats" is clicked
function viewPlayerDetails(playerName) {
    const playerStats = statsData.find((p) => p["Name"] === playerName);
    const playerRoster = rosterData.find((p) => p["full_name"] === playerName);

    const playerDetails = document.getElementById("stats-display");
    const backButtonContainer = document.getElementById("back-button-container");
    const playerList = document.querySelector(".player-list");

    if (!playerStats || !playerRoster) {
        playerDetails.innerHTML = `<p>Player stats not found.</p>`;
        return;
    }

    const playerId = playerRoster["player_id"];
    const playerImage = `https://assets.leaguestat.com/ohl/240x240/${playerId}.jpg`;

    playerDetails.innerHTML = `
        <div class="player-details-box">
            <div class="player-photo-section">
                <img src="${playerImage}" alt="${playerName}" class="player-photo-large" onerror="this.src=''; this.alt='No photo available';">
            </div>
            <div class="player-stats-section">
                <h3>${playerName}</h3>
                <p><strong>Team:</strong> ${playerRoster["team_name"]}</p>
                <p><strong>Games Played:</strong> ${playerStats["GP"]}</p>
                <p><strong>Goals:</strong> ${playerStats["G"]}</p>
                <p><strong>Assists:</strong> ${playerStats["A"]}</p>
                <p><strong>Points:</strong> ${playerStats["PTS"]}</p>
                <p><strong>Position:</strong> ${playerRoster["pos"]}</p>
            </div>
        </div>
    `;

    // Hide the team player list and show the back button
    playerList.style.display = "none";
    backButtonContainer.style.display = "block";
}

// Function to go back to the full team player list
function showTeamPlayers() {
    const playerDetails = document.getElementById("stats-display");
    const backButtonContainer = document.getElementById("back-button-container");
    const playerList = document.querySelector(".player-list");

    // Clear the player details, hide the back button, and show the team player list
    playerDetails.innerHTML = "";
    backButtonContainer.style.display = "none";
    playerList.style.display = "grid";

    // Reload the player list for the currently selected team
    const selectedTeam = document.getElementById("team-filter").value;
    if (selectedTeam) {
        filterPlayersByTeam(selectedTeam);
    }
}

// Function to filter players by team
function filterPlayersByTeam(teamName) {
    const playerList = document.querySelector(".player-list");
    const noResults = document.getElementById("no-results");

    // Clear existing players
    playerList.innerHTML = "";

    // Filter players based on the selected team
    const filteredPlayers = rosterData.filter((player) => player["team_name"] === teamName);

    if (filteredPlayers.length === 0) {
        noResults.style.display = "block";
        playerList.style.display = "none";
        return;
    }

    noResults.style.display = "none";
    playerList.style.display = "grid";

    // Populate the player list
    filteredPlayers.forEach((player) => {
        const playerCard = document.createElement("div");
        playerCard.classList.add("player-card");
        playerCard.innerHTML = `
            <img src="https://assets.leaguestat.com/ohl/240x240/${player["player_id"]}.jpg" alt="${player["full_name"]}" class="player-photo" onerror="this.src=''; this.alt='No photo available';">
            <p class="player-name">${player["full_name"]}</p>
            <p class="player-info">Position: ${player["pos"]}</p>
            <button onclick="viewPlayerDetails('${player["full_name"]}')">Get Stats</button>
        `;
        playerList.appendChild(playerCard);
    });
}

// Add event listener to the back button
document.getElementById("back-button").addEventListener("click", showTeamPlayers);


      
      
  
    // Initialize the page
    async function init() {
      statsData = await loadCSV(statsFilePath);
      rosterData = await loadCSV(rostersFilePath);
  
      populateTeams();
  
      teamFilter.addEventListener("change", filterPlayers);
      playerSearch.addEventListener("input", filterPlayers);
    }
  
    function toggleMobileMenu() {
        const mobileMenu = document.getElementById("mobileMenu");
        if (mobileMenu.style.display === "flex") {
          mobileMenu.style.display = "none";
        } else {
          mobileMenu.style.display = "flex";
        }
      }
      

    init();
  });
  