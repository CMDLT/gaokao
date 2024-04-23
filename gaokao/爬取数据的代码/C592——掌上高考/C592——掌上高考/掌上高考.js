const CryptoJs = require('crypto-js')


f = "D23ABC@#56"
// page是python进行传递
j = "api.zjzw.cn/web/api/?keyword=&page=8&province_id=&ranktype=&request_type=1&size=20&top_school_id=[3238]&type=&uri=apidata/api/gkv3/school/lists"

function v(t,a) {
    var n = f;
    t = a.replace(/^\/|https?:\/\/\/?/, ""),
    t = decodeURI(t),
    n = CryptoJs.HmacSHA1(CryptoJs.enc.Utf8.parse(t), n),
    n = CryptoJs.enc.Base64.stringify(n).toString();
    hash = CryptoJs.MD5(n).toString()
    return hash
}

l = v({
    SIGN: f
},j)

console.log(l)

