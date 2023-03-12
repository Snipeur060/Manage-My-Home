if (typeof jQuery === "undefined") {
    throw new Error("jQuery plugins need to be before this file");
}
$(function () {
    "use strict";
    let root = document.documentElement;
    $(".menu-toggle").on("click", function () {
        $(".sidebar").toggleClass("open");
        $("#layout-l .menu").toggleClass("open");
    });
    $(".megamenu-toggle").on("click", function () {
        $(".menu").toggleClass("open");
    });
    $(".sidebar-mini-btn").on("click", function () {
        $(".sidebar").toggleClass("sidebar-mini");
    });
    $(".chatlist-toggle").on("click", function () {
        $(".card-chat").toggleClass("open");
    });
    $(".theme-rtl input:checkbox").on("click", function () {
        if ($(this).is(":checked")) {
            $("body").addClass("rtl_mode");
        } else {
            $("body").removeClass("rtl_mode");
        }
    });
    $(".main-search input").on("focus", function () {
        $(".search-result").addClass("show");
    });
    $(".main-search input").on("blur", function () {
        $(".search-result").removeClass("show");
    });
    $(".font_setting input:radio").on("click", function () {
        var others = $("[name='" + this.name + "']")
            .map(function () {
                return this.value;
            })
            .get()
            .join(" ");
        console.log(others);
        $("body").removeClass(others).addClass(this.value);
    });
    if (document.getElementById("NotificationsDiv")) {
        document.getElementById("NotificationsDiv").addEventListener("click", function (event) {
            event.stopPropagation();
        });
    }
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});
$(function () {
    "use strict";
    let root = document.documentElement;
    $(".choose-skin li").on("click", function () {
        var $body = $("#layout-a, #layout-b, #layout-c, #layout-d, #layout-d-sub-header, #layout-e, #layout-f, #layout-g, #layout-h,  #layout-i, #layout-j, #layout-k, #layout-l, #layout-m, #layout-p, #layout-n, #layout-q, #layout-o");
        var $this = $(this);
        var existTheme = $(".choose-skin li.active").data("theme");
        $(".choose-skin li").removeClass("active");
        $body.removeClass("theme-" + existTheme);
        $this.addClass("active");
        $body.addClass("theme-" + $this.data("theme"));
    });
    $(".gradient-switch input:checkbox").on("click", function () {
        if ($(this).is(":checked")) {
            $(".sidebar").addClass("gradient");
        } else {
            $(".sidebar").removeClass("gradient");
        }
    });
    $(".imagebg-switch input:checkbox").on("click", function () {
        if ($(this).is(":checked")) {
            $(".bg-images").addClass("show");
            $(".sidebar").addClass("sidebar-img-bg");
        } else {
            $(".bg-images").removeClass("show");
            $(".sidebar").removeClass("sidebar-img-bg");
        }
    });
    $("#primaryColorPicker")
        .colorpicker()
        .on("changeColor", function () {
            root.style.setProperty("--primary-color", $(this).colorpicker("getValue", "#ffffff"));
        });
    $("#secondaryColorPicker")
        .colorpicker()
        .on("changeColor", function () {
            root.style.setProperty("--secondary-color", $(this).colorpicker("getValue", "#ffffff"));
        });
    $("#chartColorPicker1")
        .colorpicker()
        .on("changeColor", function () {
            root.style.setProperty("--chart-color1", $(this).colorpicker("getValue", "#ffffff"));
        });
    $("#chartColorPicker2")
        .colorpicker()
        .on("changeColor", function () {
            root.style.setProperty("--chart-color2", $(this).colorpicker("getValue", "#ffffff"));
        });
    $("#chartColorPicker3")
        .colorpicker()
        .on("changeColor", function () {
            root.style.setProperty("--chart-color3", $(this).colorpicker("getValue", "#ffffff"));
        });
    $("#chartColorPicker4")
        .colorpicker()
        .on("changeColor", function () {
            root.style.setProperty("--chart-color4", $(this).colorpicker("getValue", "#ffffff"));
        });
    $("#chartColorPicker5")
        .colorpicker()
        .on("changeColor", function () {
            root.style.setProperty("--chart-color5", $(this).colorpicker("getValue", "#ffffff"));
        });
});
$(function () {
    "use strict";
    var toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
    var toggleHcSwitch = document.querySelector('.theme-high-contrast input[type="checkbox"]');
    var currentTheme = localStorage.getItem("theme");
    if (currentTheme) {
        document.documentElement.setAttribute("data-theme", currentTheme);
        if (currentTheme === "dark") {
            toggleSwitch.checked = true;
        }
        if (currentTheme === "high-contrast") {
            toggleHcSwitch.checked = true;
            toggleSwitch.checked = false;
        }
    }
    function switchTheme(e) {
        if (e.target.checked) {
            document.documentElement.setAttribute("data-theme", "dark");
            localStorage.setItem("theme", "dark");
            $('.theme-high-contrast input[type="checkbox"]').prop("checked", false);
        } else {
            document.documentElement.setAttribute("data-theme", "light");
            localStorage.setItem("theme", "light");
        }
    }
    function switchHc(e) {
        if (e.target.checked) {
            document.documentElement.setAttribute("data-theme", "high-contrast");
            localStorage.setItem("theme", "high-contrast");
            $('.theme-switch input[type="checkbox"]').prop("checked", false);
        } else {
            document.documentElement.setAttribute("data-theme", "light");
            localStorage.setItem("theme", "light");
        }
    }
    toggleSwitch.addEventListener("change", switchTheme, false);
    toggleHcSwitch.addEventListener("change", switchHc, false);
});
