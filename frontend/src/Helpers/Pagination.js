export function getPaginationItems(paginate, setUrl = true) {
    if (!paginate?.last_page) return [];
    // console.log(paginate);
    const current = paginate.current_page;
    setPageURL(current, setUrl);
    const last = paginate.last_page;
    const numBtn = (num) => ({ type: 'number', value: num, active: num === current });

    if (last <= 7) {
        return Array.from({ length: last }, (_, i) => numBtn(i + 1));
    }

    let items = [numBtn(1)];

    if (current < 5) {
        items.push(...[2, 3, 4, 5].map(numBtn), { type: 'dots' });
    } else if (current > last - 4) {
        items.push({ type: 'dots' }, ...[last - 4, last - 3, last - 2, last - 1].map(numBtn));
    } else {
        items.push(
            { type: 'dots' },
            ...[current - 1, current, current + 1].map(numBtn),
            { type: 'dots' }
        );
    }

    if (last > 1) items.push(numBtn(last));

    return items;
}

export function getPageUrl(paginate, page) {
    if (!paginate?.links) return null;
    const link = paginate.links.find(link => link.label == page);
    return link?.url || null;
}

function setPageURL(page, setUrl = true) {
    if (!setUrl) return;
    const url = new URL(window.location.href);
    if (page === 1) {
        url.searchParams.delete('page');
    } else {
        url.searchParams.set('page', page);
    }
    window.history.pushState({}, '', url);
}
