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

export function getStateBadge(state) {
    switch(state) {
        case STATE_DRAFT: return <span className="badge badge-warning">مسودة</span>;
        case STATE_ACCEPTED: return <span className="badge badge-success">مقبول</span>;
        case STATE_REJECTED: return <span className="badge badge-error">مرفوض</span>;
        default: return <span className="badge">غير معروف</span>;
    }
}
