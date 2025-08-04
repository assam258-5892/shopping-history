// static/js/select-nearest-store.js
// 현위치에서 가장 가까운 매장 자동 선택
function getDistance(lat1, lng1, lat2, lng2) {
    function toRad(x) { return x * Math.PI / 180; }
    var R = 6371; // km
    var dLat = toRad(lat2-lat1);
    var dLng = toRad(lng2-lng1);
    var a = Math.sin(dLat/2)*Math.sin(dLat/2) + Math.cos(toRad(lat1))*Math.cos(toRad(lat2))*Math.sin(dLng/2)*Math.sin(dLng/2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}
window.addEventListener('DOMContentLoaded', function() {
    var sel = document.getElementById('store_code');
    if (!sel) return;
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(pos) {
            var myLat = pos.coords.latitude;
            var myLng = pos.coords.longitude;
            var minDist = Infinity, minIdx = -1;
            for (var i=0; i<sel.options.length; i++) {
                var opt = sel.options[i];
                var lat = parseFloat(opt.getAttribute('data-lat'));
                var lng = parseFloat(opt.getAttribute('data-lng'));
                if (!isNaN(lat) && !isNaN(lng)) {
                    var dist = getDistance(myLat, myLng, lat, lng);
                    if (dist < minDist) { minDist = dist; minIdx = i; }
                }
            }
            if (minIdx >= 0) sel.selectedIndex = minIdx;
        });
    }
});
