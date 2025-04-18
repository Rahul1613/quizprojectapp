<?php
// Exam Slot Booking Interface
// Enhanced with Solo Leveling inspired holographic UI

// Include necessary files
include('header.php');

// Main container with particle effect background
echo '<div class="holographic-container" id="particles-js">';

// Enhanced status window with progress bar
echo '<div class="status-window">';
echo '<h2 class="neon-text">Exam Slot Booking</h2>';
echo '<div id="booking-status">Select a slot to begin</div>';
echo '<div class="progress-bar"><div class="progress"></div></div>';
echo '</div>';

// Slot grid with 3D floating effect
echo '<div class="slot-grid">';
// Example slot cards
for ($i = 1; $i <= 6; $i++) {
    echo '<div class="holographic-card" onclick="selectSlot(this)">';
    echo '<div class="card-content">';
    echo '<h3 class="neon-text">Slot '.$i.'</h3>';
    echo '<p>Date: 2025-03-'.(15+$i).'</p>';
    echo '<p>Time: 10:00 AM</p>';
    echo '</div>';
    echo '</div>';
}
echo '</div>';

// Footer
echo '</div>';
include('footer.php');
?>

<style>
/* Enhanced Holographic UI Styles */
.holographic-container {
    position: relative;
    min-height: 100vh;
    padding: 2rem;
}

#particles-js {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    z-index: -1;
}

.neon-text {
    color: #fff;
    text-shadow: 0 0 5px #00ffff, 0 0 10px #00ffff, 0 0 20px #00ffff;
}

.holographic-card {
    background: rgba(0,255,255,0.1);
    border: 1px solid rgba(0,255,255,0.3);
    padding: 1.5rem;
    margin: 1rem;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.3s ease;
    transform: perspective(1000px) rotateY(0deg);
    box-shadow: 0 0 15px rgba(0,255,255,0.3);
}

.holographic-card:hover {
    transform: perspective(1000px) rotateY(15deg) scale(1.05);
    box-shadow: 0 0 25px rgba(0,255,255,0.7);
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: perspective(1000px) rotateY(15deg) translateY(0); }
    50% { transform: perspective(1000px) rotateY(15deg) translateY(-10px); }
}

.slot-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    position: relative;
    z-index: 1;
}

.status-window {
    background: rgba(0,0,0,0.7);
    padding: 1.5rem;
    margin-bottom: 2rem;
    border-radius: 15px;
    border: 1px solid rgba(0,255,255,0.3);
    box-shadow: 0 0 20px rgba(0,255,255,0.2);
}

.progress-bar {
    width: 100%;
    height: 5px;
    background: rgba(255,255,255,0.1);
    border-radius: 5px;
    margin-top: 1rem;
}

.progress {
    height: 100%;
    width: 0;
    background: linear-gradient(90deg, #00ffff, #00ff88);
    border-radius: 5px;
    transition: width 0.3s ease;
}
</style>

<script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
<script>
// Initialize particles background
particlesJS.load('particles-js', 'particles.json', function() {
    console.log('Particles.js config loaded');
});

// Enhanced slot selection function
function selectSlot(element) {
    document.querySelectorAll('.holographic-card').forEach(card => {
        card.classList.remove('active');
    });

    element.classList.add('active');
    const slotInfo = element.querySelector('.card-content').innerText;
    document.getElementById('booking-status').innerHTML = `Selected Slot:<br>${slotInfo}`;
    document.querySelector('.progress').style.width = '100%';
    showPopup('Slot selected successfully!');
}

// Enhanced popup notification
function showPopup(message) {
    const popup = document.createElement('div');
    popup.className = 'holographic-popup';
    popup.innerText = message;
    document.body.appendChild(popup);

    setTimeout(() => {
        popup.style.opacity = '0';
        setTimeout(() => {
            popup.remove();
        }, 300);
    }, 2700);
}
</script>
