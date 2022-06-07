if ('serviceWorker' in navigator) {
2
    window.addEventListener('load', function() {
3
        navigator.serviceWorker
4
        .register('/wtgw/static/serviceworker.js', {scope: '/wtgw/'})
5
        .then(function(registration) {
6
            console.log('ServiceWorker registration successful with scope: ', registration.scope);
7
        }, function(err) {
8
            console.log('ServiceWorker registration failed: ', err);
9
        });
10
    });
11
}