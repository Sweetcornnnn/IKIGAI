// ─── Chat State ───
let isChatOpen = false;
let currentUserId = null;
let username = null;
let pollingInterval = null;

// ─── Profile & DM State ───
let profileUserId = null;
let dmUserId = null;
let dmPollingInterval = null;

// ─── DOM Elements ───
const chatToggle = document.getElementById('chatToggle');
const chatPanel = document.getElementById('chatPanel');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const chatSendBtn = document.getElementById('chatSendBtn');
const chatBadge = document.getElementById('chatBadge');
const usersContainer = document.getElementById('usersContainer');
const chatOverlay = document.getElementById('chatOverlay');

// Profile Modal
const profileModal = document.getElementById('profileModal');
const profileAvatar = document.getElementById('profileAvatar');
const profileUsername = document.getElementById('profileUsername');
const profileBio = document.getElementById('profileBio');
const profileJoinDate = document.getElementById('profileJoinDate');
const profileXp = document.getElementById('profileXp');
const profileLevel = document.getElementById('profileLevel');
const profileStreak = document.getElementById('profileStreak');
const profileAchievements = document.getElementById('profileAchievements');
const profileAchievementCount = document.getElementById('profileAchievementCount');

// DM Modal
const dmModal = document.getElementById('dmModal');
const dmMessages = document.getElementById('dmMessages');
const dmInput = document.getElementById('dmInput');
const dmSendBtn = document.getElementById('dmSendBtn');
const dmUsername = document.getElementById('dmUsername');
const dmAvatar = document.getElementById('dmAvatar');

// ─── Get CSRF Token ───
function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ─── Get User Info ───
function getUserInfo() {
    return {
        userId: window.CHAT_USER_ID || null,
        username: window.CHAT_USERNAME || null
    };
}

// ─── Send Public Message ───
function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    const csrftoken = getCsrfToken();
    const formData = new FormData();
    formData.append('message', message);

    fetch('/chat/send/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken || '',
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            chatInput.value = '';
            displayMessage(data.message);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } else {
            console.error('Error sending message:', data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

// ─── Load Public Messages ───
function loadMessages() {
    fetch('/chat/messages/')
        .then(response => response.json())
        .then(data => {
            if (data.messages && data.messages.length > 0) {
                const currentCount = chatMessages.children.length;
                if (data.messages.length !== currentCount) {
                    chatMessages.innerHTML = '';
                    data.messages.forEach(msg => {
                        displayMessage(msg, false);
                    });
                    if (isChatOpen) {
                        chatMessages.scrollTop = chatMessages.scrollHeight;
                    }
                }
            }
        })
        .catch(error => console.error('Error loading messages:', error));
}

// ─── Load Users ───
function loadUsers() {
    fetch('/chat/users/')
        .then(response => response.json())
        .then(data => {
            if (data.users) {
                usersContainer.innerHTML = '';
                data.users.forEach(user => {
                    const userEl = document.createElement('div');
                    userEl.className = 'user-item';
                    userEl.innerHTML = `
                        <div class="avatar">
                            ${user.avatar ? `<img src="${user.avatar}" alt="${user.username}">` : user.username.charAt(0).toUpperCase()}
                        </div>
                        <div class="user-info">
                            <span class="username">${user.username}</span>
                            <span class="online-status">
                                <span class="online-dot ${user.is_online ? 'online' : ''}"></span>
                                ${user.is_online ? 'Online' : 'Offline'}
                            </span>
                        </div>
                    `;
                    userEl.addEventListener('click', function() {
                        openProfileModal(user.id);
                    });
                    usersContainer.appendChild(userEl);
                });
            }
        })
        .catch(error => console.error('Error loading users:', error));
}

// ─── Display Public Message ───
function displayMessage(data, animate = true) {
    const isOwn = data.user_id === currentUserId;

    const wrapper = document.createElement('div');
    wrapper.className = `message-wrapper ${isOwn ? 'own' : 'other'}`;

    // Avatar (clickable)
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.textContent = data.username.charAt(0).toUpperCase();
    avatarDiv.addEventListener('click', function(e) {
        e.stopPropagation();
        openProfileModal(data.user_id);
    });

    // Content container
    const content = document.createElement('div');
    content.className = 'message-content';

    // Sender name (clickable)
    const senderSpan = document.createElement('span');
    senderSpan.className = 'message-sender';
    senderSpan.textContent = data.username;
    senderSpan.addEventListener('click', function(e) {
        e.stopPropagation();
        openProfileModal(data.user_id);
    });

    // Message bubble
    const bubble = document.createElement('div');
    bubble.className = `message-bubble ${isOwn ? 'own' : 'other'}`;
    bubble.textContent = data.message;

    // Time
    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    timeSpan.textContent = formatTime(data.timestamp);

    // Assemble – for own messages, put avatar first then content (flex-direction: row-reverse will swap them)
    if (isOwn) {
        wrapper.appendChild(avatarDiv);
        content.appendChild(senderSpan);
        content.appendChild(bubble);
        content.appendChild(timeSpan);
        wrapper.appendChild(content);
    } else {
        wrapper.appendChild(avatarDiv);
        content.appendChild(senderSpan);
        content.appendChild(bubble);
        content.appendChild(timeSpan);
        wrapper.appendChild(content);
    }

    chatMessages.appendChild(wrapper);

    if (animate) {
        wrapper.style.opacity = '0';
        wrapper.style.transform = 'translateY(10px)';
        setTimeout(() => {
            wrapper.style.transition = 'all 0.2s ease';
            wrapper.style.opacity = '1';
            wrapper.style.transform = 'translateY(0)';
        }, 10);
    }
}

// ─── Display Private Message ───
function displayDmMessage(data, animate = true) {
    const isOwn = data.user_id === currentUserId;
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${isOwn ? 'own' : 'other'}`;

    if (!isOwn) {
        msgDiv.innerHTML = `<div class="sender">${data.username}</div>`;
    }
    msgDiv.innerHTML += `<div>${data.message}</div>`;
    msgDiv.innerHTML += `<div class="time">${formatTime(data.timestamp)}</div>`;

    dmMessages.appendChild(msgDiv);

    if (animate) {
        msgDiv.style.opacity = '0';
        msgDiv.style.transform = 'translateY(10px)';
        setTimeout(() => {
            msgDiv.style.transition = 'all 0.2s ease';
            msgDiv.style.opacity = '1';
            msgDiv.style.transform = 'translateY(0)';
        }, 10);
    }
}

// ─── Format Time ───
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);

    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return date.toLocaleDateString();
}

// ─── Profile Card Modal ───
function openProfileModal(userId) {
    profileUserId = userId;
    profileModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';

    fetch(`/accounts/profile/${userId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error loading profile: ' + data.error);
                return;
            }

            if (data.avatar) {
                profileAvatar.innerHTML = `<img src="${data.avatar}" style="width: 100%; height: 100%; object-fit: cover;">`;
            } else {
                profileAvatar.textContent = data.username.charAt(0).toUpperCase();
            }

            profileUsername.textContent = data.username;
            profileBio.textContent = data.bio || 'No bio yet.';
            profileJoinDate.textContent = `Joined ${data.join_date}`;
            profileXp.textContent = data.xp;
            profileLevel.textContent = data.level;
            profileStreak.textContent = data.streak_days;
            profileAchievementCount.textContent = `${data.achievement_count} unlocked`;

            if (data.achievements && data.achievements.length > 0) {
                profileAchievements.innerHTML = '';
                data.achievements.forEach(ach => {
                    const span = document.createElement('span');
                    span.title = ach.name;
                    span.textContent = ach.icon;
                    profileAchievements.appendChild(span);
                });
            } else {
                profileAchievements.innerHTML = '<span style="color: var(--text-muted); font-size: 12px; padding: 8px 0;">No achievements yet</span>';
            }
        })
        .catch(error => {
            console.error('Error loading profile:', error);
            alert('Could not load profile.');
        });
}

function closeProfileModal() {
    profileModal.style.display = 'none';
    document.body.style.overflow = '';
    profileUserId = null;
}

// ─── Private Chat ───
function openPrivateChat() {
    if (!profileUserId) return;

    fetch(`/accounts/profile/${profileUserId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }

            dmUserId = profileUserId;
            dmUsername.textContent = data.username;
            if (data.avatar) {
                dmAvatar.innerHTML = `<img src="${data.avatar}" style="width: 100%; height: 100%; object-fit: cover;">`;
            } else {
                dmAvatar.textContent = data.username.charAt(0).toUpperCase();
            }

            closeProfileModal();
            dmModal.style.display = 'flex';
            document.body.style.overflow = 'hidden';

            loadDmMessages();

            if (dmPollingInterval) {
                clearInterval(dmPollingInterval);
            }
            dmPollingInterval = setInterval(loadDmMessages, 3000);
        })
        .catch(error => {
            console.error('Error opening private chat:', error);
            alert('Could not open private chat.');
        });
}

function closeDmModal() {
    dmModal.style.display = 'none';
    document.body.style.overflow = '';
    dmUserId = null;
    if (dmPollingInterval) {
        clearInterval(dmPollingInterval);
        dmPollingInterval = null;
    }
}

// ─── Load Private Messages ───
function loadDmMessages() {
    if (!dmUserId) return;

    fetch(`/chat/private/${dmUserId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.messages) {
                const currentCount = dmMessages.children.length;
                if (data.messages.length !== currentCount) {
                    dmMessages.innerHTML = '';
                    data.messages.forEach(msg => {
                        displayDmMessage(msg, false);
                    });
                    dmMessages.scrollTop = dmMessages.scrollHeight;
                }
            }
        })
        .catch(error => console.error('Error loading private messages:', error));
}

// ─── Send Private Message ───
function sendDmMessage() {
    const message = dmInput.value.trim();
    if (!message || !dmUserId) return;

    const csrftoken = getCsrfToken();
    const formData = new FormData();
    formData.append('message', message);
    formData.append('recipient_id', dmUserId);

    fetch('/chat/private/send/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken || '',
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            dmInput.value = '';
            displayDmMessage(data.message);
            dmMessages.scrollTop = dmMessages.scrollHeight;
        } else {
            console.error('Error sending private message:', data.error);
        }
    })
    .catch(error => console.error('Error:', error));
}

// ─── Close Chat ───
function closeChat() {
    if (!isChatOpen) return;
    isChatOpen = false;
    chatPanel.classList.remove('open');
    chatOverlay.classList.remove('active');
    const icon = document.getElementById('chatIcon');
    if (icon) icon.classList.remove('active');
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}

// ─── Open Chat ───
function openChat() {
    if (isChatOpen) return;
    isChatOpen = true;
    chatPanel.classList.add('open');
    chatOverlay.classList.add('active');
    const icon = document.getElementById('chatIcon');
    if (icon) icon.classList.add('active');
    chatBadge.style.display = 'none';
    loadMessages();
    chatMessages.scrollTop = chatMessages.scrollHeight;
    if (!pollingInterval) {
        pollingInterval = setInterval(loadMessages, 3000);
    }
}

// ─── Toggle Chat Panel ───
function toggleChat() {
    if (isChatOpen) {
        closeChat();
    } else {
        openChat();
    }
}

// ─── Close chat when clicking outside (on overlay) ───
chatOverlay.addEventListener('click', function() {
    closeChat();
});

// ─── Close modals and chat on Escape ───
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        if (dmModal.style.display === 'flex') {
            closeDmModal();
        } else if (profileModal.style.display === 'flex') {
            closeProfileModal();
        } else if (isChatOpen) {
            closeChat();
        }
    }
});

// ─── Initialize ───
document.addEventListener('DOMContentLoaded', function() {
    const user = getUserInfo();
    if (!user.userId) {
        console.log('⚠️ User not logged in. Chat disabled.');
        return;
    }

    currentUserId = user.userId;
    username = user.username;

    chatToggle.addEventListener('click', function(e) {
        e.stopPropagation();
        toggleChat();
    });

    chatSendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });

    dmSendBtn.addEventListener('click', sendDmMessage);
    dmInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendDmMessage();
    });

    loadMessages();
    loadUsers();

    setInterval(loadUsers, 30000);
});