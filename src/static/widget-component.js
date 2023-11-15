document.addEventListener("DOMContentLoaded", function () {
    const comment_box = document.getElementById('pommento-box')
    const domain = comment_box.dataset.domain
    const site =  comment_box.dataset.site
    const page = comment_box.dataset.page

    comment_box.innerHTML = `
    <iframe frameborder="0" width="100%" scrolling="yes" height="100%" src="${domain}/comment-widget?site_id=${site}&page_id=${page}" title="Pommento Comment">
    </iframe>
    `
  });