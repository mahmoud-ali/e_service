export function getCookie(name) {
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

export const csrftoken = getCookie('csrftoken');

export const STATE_DRAFT = 1;
export const STATE_ACCEPTED = 2;
export const STATE_REJECTED = 3;

export function getStateInfo(state) {
    switch(state) {
        case STATE_DRAFT: return { label: 'مسودة', className: 'badge-warning' };
        case STATE_ACCEPTED: return { label: 'مقبول', className: 'badge-success' };
        case STATE_REJECTED: return { label: 'مرفوض', className: 'badge-error' };
        default: return { label: 'غير معروف', className: '' };
    }
}
