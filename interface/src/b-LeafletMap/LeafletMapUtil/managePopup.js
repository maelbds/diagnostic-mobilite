const L = window.L;

// --------------------------------   POPUP  ----------------------------------------
export function managePopup(element, content){
  /*
  let popup = L.popup({autoPan: false
    })
      .setLatLng(element.latlng)
      .setContent(content);
  element.bindPopup(popup);
  element.on('mouseover', function (e) {
      this.openPopup();
  });
  element.on('mouseout', function (e) {
      this.closePopup();
  });*/


  let popup = L.popup({autoPan: false});
  popup.setContent(content);
  element.bindPopup(popup);

  element.on('mouseover', function (e) {
    let popup = e.target.getPopup();
    popup.setLatLng(e.latlng);
    e.target.openPopup(popup)
  });

  element.on('mouseout', function(e) {
     e.target.closePopup();
  });

  element.on('mousemove', function (e) {
    e.target.closePopup();
    let popup = e.target.getPopup();
    popup.setLatLng(e.latlng);
    e.target.openPopup(popup);
  });
}
