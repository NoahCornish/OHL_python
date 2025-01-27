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
    function viewPlayerDetails(playerName) {
        const playerStats = statsData.find((p) => p["Name"] === playerName);
        const playerRoster = rosterData.find((p) => p["full_name"] === playerName);
      
        if (!playerStats || !playerRoster) {
          statsDisplay.innerHTML = `<p>Player stats not found.</p>`;
          return;
        }
      
        const playerId = playerRoster["player_id"];
        const playerImage = `https://assets.leaguestat.com/ohl/240x240/${playerId}.jpg`;
      
        statsDisplay.innerHTML = `
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
      }
      
      
  
    // Initialize the page
    async function init() {
      statsData = await loadCSV(statsFilePath);
      rosterData = await loadCSV(rostersFilePath);
  
      populateTeams();
  
      teamFilter.addEventListener("change", filterPlayers);
      playerSearch.addEventListener("input", filterPlayers);
    }
  
    init();
  });
  