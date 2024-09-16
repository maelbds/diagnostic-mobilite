//export const api_url = "http://127.0.0.1:5000/api/main/"
export const api_url = "https://diagnostic-mobilite.fr/api/main/"


export function api_call(endpoints){
  let myHeaders = new Headers()
  myHeaders.append("Accept", "application/json");
  myHeaders.append("Content-Type", "application/json");
  myHeaders.append("Access-Control-Allow-Origin", "*");
  myHeaders.append("Cache-Control", "max-age=604800");
  myHeaders.append("withCredentials", "true");

  let request_params = {method: "GET", headers: myHeaders};

  let com_codes = this.props.geography.com.map((c) => c.geo_code)
  let geo_codes_param = `geo_codes=${com_codes.join(",")}`

  Promise.all(endpoints.map((e) =>
      fetch(`${api_url}${e}?${geo_codes_param}`, request_params)
  )).then((responses) => {
    responses.forEach((response, i) => {
      if (response.status !== 200){ throw new Error(response.statusText); }
    });
    return Promise.all(responses.map(r => r.json()))
  }).then((responses) => {
    this.setState({
      status: "loaded",
      data: Object.assign(...responses)
    })
  }).catch((err) => {
    this.setState({
      status: "error",
      error: err.message
    });
  })
}
