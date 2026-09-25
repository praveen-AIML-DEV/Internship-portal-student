// Global Client-side Utilities for Smart Academia-Industry Collaboration Portal

document.addEventListener('DOMContentLoaded', () => {
    initNotifications();
});

function initNotifications() {
    const notifBtn = document.getElementById('notifBtn');
    const notifMenu = document.getElementById('notifMenu');

    if (notifBtn && notifMenu) {
        notifBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            notifMenu.classList.toggle('hidden');
            loadNotifications();
        });

        document.addEventListener('click', (e) => {
            if (!notifMenu.contains(e.target) && e.target !== notifBtn) {
                notifMenu.classList.add('hidden');
            }
        });
    }
}

async function loadNotifications() {
    const list = document.getElementById('notifList');
    if (!list) return;

    try {
        const res = await fetch('/api/notifications');
        const notifs = await res.json();
        if (notifs && notifs.length > 0) {
            list.innerHTML = notifs.map(n => `
                <div class="p-2.5 rounded-xl ${n.is_read ? 'bg-slate-50 border border-slate-100' : 'bg-indigo-50/80 border border-indigo-100'} transition">
                    <div class="flex items-center justify-between">
                        <p class="font-semibold text-slate-800 text-xs">${n.title}</p>
                        <span class="text-[10px] text-slate-400">${n.time_ago || ''}</span>
                    </div>
                    <p class="text-slate-600 text-[11px] mt-0.5">${n.message}</p>
                </div>
            `).join('');
        } else {
            list.innerHTML = '<p class="text-slate-400 text-center py-4 text-xs">No notifications yet.</p>';
        }
    } catch (err) {
        console.error('Failed to load notifications:', err);
    }
}

// Global Toast Messenger
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    const colorClass = type === 'success' ? 'bg-emerald-600 text-white' : (type === 'danger' ? 'bg-rose-600 text-white' : 'bg-indigo-600 text-white');
    toast.className = `fixed bottom-5 right-5 px-4 py-3 rounded-xl shadow-xl text-sm font-medium z-50 flex items-center space-x-2 transition-all duration-300 transform translate-y-2 opacity-0 ${colorClass}`;
    toast.innerHTML = `<i class="fa-solid ${type === 'success' ? 'fa-check-circle' : 'fa-info-circle'}"></i> <span>${message}</span>`;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.remove('translate-y-2', 'opacity-0');
    }, 50);

    setTimeout(() => {
        toast.classList.add('translate-y-2', 'opacity-0');
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}
