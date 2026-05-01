(function () {
  // 배포 후 실제 API 서버 주소로 변경하세요
  var API_BASE = "https://your-api-url.railway.app";

  var SKIN_TYPES = ["전체", "민감성", "건성", "지성", "복합성", "아토피"];

  function init() {
    var container = document.getElementById("skin-filter-widget");
    if (!container) return;

    var productNo = container.getAttribute("data-product-no");

    var buttons = SKIN_TYPES.map(function (type, i) {
      return (
        '<button class="sfb' +
        (i === 0 ? " sfb-active" : "") +
        '" data-type="' +
        type +
        '" onclick="SkinFilter.select(this,\'' +
        type +
        "\','" +
        productNo +
        "'\">" +
        type +
        "</button>"
      );
    }).join("");

    container.innerHTML =
      '<div class="sf-wrap">' +
      '<p class="sf-title">내 피부 타입에 맞는 리뷰 보기</p>' +
      '<div class="sf-btns">' +
      buttons +
      "</div>" +
      '<div id="sf-results"></div>' +
      "</div>";

    injectStyles();
    loadReviews(null, productNo);
  }

  function injectStyles() {
    if (document.getElementById("sf-styles")) return;
    var s = document.createElement("style");
    s.id = "sf-styles";
    s.textContent = [
      ".sf-wrap{margin:20px 0;padding:16px;border:1px solid #eee;border-radius:8px}",
      ".sf-title{font-weight:700;margin-bottom:12px;color:#333;font-size:14px}",
      ".sf-btns{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}",
      ".sfb{padding:6px 14px;border:1px solid #ccc;border-radius:20px;background:#fff;cursor:pointer;font-size:13px;transition:all .2s}",
      ".sfb.sfb-active{background:#3d3d3d;color:#fff;border-color:#3d3d3d}",
      ".sfb:hover{border-color:#3d3d3d}",
      ".sf-item{padding:12px 0;border-bottom:1px solid #f0f0f0}",
      ".sf-text{font-size:14px;color:#444;line-height:1.6}",
      ".sf-tags{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px}",
      ".sf-tag{font-size:11px;padding:2px 8px;background:#f5f5f5;border-radius:10px;color:#666}",
      ".sf-empty{color:#999;font-size:14px;text-align:center;padding:20px}",
    ].join("");
    document.head.appendChild(s);
  }

  function loadReviews(skinType, productNo) {
    var el = document.getElementById("sf-results");
    if (!el) return;
    el.innerHTML = '<p style="color:#999;font-size:13px">불러오는 중...</p>';

    var url = API_BASE + "/reviews?";
    if (skinType && skinType !== "전체") url += "skin_type=" + encodeURIComponent(skinType) + "&";
    if (productNo) url += "product_no=" + encodeURIComponent(productNo);

    fetch(url)
      .then(function (r) { return r.json(); })
      .then(function (data) { renderReviews(data.reviews || [], el); })
      .catch(function () {
        el.innerHTML = '<p class="sf-empty">리뷰를 불러올 수 없습니다.</p>';
      });
  }

  function renderReviews(reviews, container) {
    if (!reviews.length) {
      container.innerHTML = '<p class="sf-empty">해당 피부 타입의 리뷰가 없습니다.</p>';
      return;
    }
    container.innerHTML = reviews
      .slice(0, 10)
      .map(function (r) {
        var text = r.review_text || "";
        var preview = text.length > 200 ? text.slice(0, 200) + "..." : text;
        var tags = (r.skin_types || [])
          .map(function (t) { return '<span class="sf-tag">🌿 ' + esc(t) + "</span>"; })
          .concat(
            (r.skin_concerns || []).map(function (c) {
              return '<span class="sf-tag">💬 ' + esc(c) + "</span>";
            })
          )
          .join("");
        return (
          '<div class="sf-item">' +
          '<p class="sf-text">' + esc(preview) + "</p>" +
          '<div class="sf-tags">' + tags + "</div>" +
          "</div>"
        );
      })
      .join("");
  }

  function esc(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  window.SkinFilter = {
    select: function (btn, type, productNo) {
      var btns = document.querySelectorAll(".sfb");
      for (var i = 0; i < btns.length; i++) btns[i].classList.remove("sfb-active");
      btn.classList.add("sfb-active");
      loadReviews(type === "전체" ? null : type, productNo);
    },
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
