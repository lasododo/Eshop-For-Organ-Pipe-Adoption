// add <script></script> for debug purpuses

$(document).ready(function () {
        var productForm = $(".product-add-form-ajax")

        productForm.submit(function (event) {
            event.preventDefault();
            var thisForm = $(this)
            var action = thisForm.attr("data-endpoint");
            // var action = thisForm.attr("action");
            var httpMethod = thisForm.attr("method");
            var formData = thisForm.serialize();

            console.log("before_ajax")
            $.ajax({
                url: action,
                method: httpMethod,
                data: formData,
                success: function (data) {
                    var submitSpan = thisForm.find(".submit-span")

                    var currentPath = window.location.href

                    console.log("before_refresh")
                    if (currentPath.indexOf("cart") !== -1) {
                        refreshCart()
                    }
                    console.log("after_refresh")

                    if (data.added) {
                        submitSpan.html('<button class="btn btn-outline-danger bg-dark btn-block"> Remove from Cart <i class="fas fa-heart-broken" aria-hidden="true"></i> </button>')
                    } else {
                        submitSpan.html('<button type="submit" class="btn btn-success btn-block">  Add to Cart <i class="fa fa-shopping-cart fa-fw" aria-hidden="true"></i> </button>')
                    }

                    var navbar_count = $(".mav-cart-count")
                    navbar_count.text(data.cartItemCount)
                },
                error: function (errorData) {
                    console.log("aaaaaaaaa")
                    console.log(errorData)
                }
            })

            function refreshCart() {
                var cartTable = $(".cart-table")
                var cartBody = cartTable.find(".cart-body")
                // cartBody.html("<h1> Changed </h1>")
                var productsRows = cartBody.find(".cart-product")
                var currentUrl = window.location.href

                var refreshCartUrl = '/api/cart/';
                var refreshCartMethod = "GET";
                var data = {};

                $.ajax({
                    url: refreshCartUrl,
                    method: refreshCartMethod,
                    data: data,
                    success: function (data) {
                        console.log("succ")
                        console.log(data)
                        var hiddenRemoveButton = $(".cart-item-remove-form")
                        console.log(data.pipes.length)
                        if (data.pipes.length > 0) {
                            productsRows.html("")
                            var i = data.pipes.length

                            $.each(data.pipes, function (index, value) {
                                var newHRB = hiddenRemoveButton.clone();
                                newHRB.css("display", "block");
                                // newHRB.removeClass("hidden-clazz")
                                newHRB.find(".cart-item-pipe-id").val(value.id);
                                var str = "<tr class=\"cart-product\">\n" +
                                "                                    <th class=\"text-center\" style=\"vertical-align: middle\"> " + i + "</th>\n" +
                                "                                    <th class=\"text-left\" style=\"vertical-align: middle\">\n" +
                                "                                        <a href=\"" + value.url + "\">\n" +
                                "                                            <h6 class=\"font_for_bold\" style=\"margin: 0; font-weight: bold\"> " + value.registry +" / " + value.note +" </h6>\n" +
                                "                                            <h6 class=\"font_for_normal\" style=\"margin: 0; font-weight: normal\"> (" + value.manual + ") </h6>\n" +
                                "                                        </a>\n" +
                                "                                    </th>\n" +
                                "                                    <th class=\"text-left\" style=\"vertical-align: middle\"> " + value.price + " CZK </th>\n" +
                                "                                    <th class=\"text-center\" style=\"vertical-align: middle\">  " + newHRB.html() + " </th>\n" +
                                "                                </tr>";
                                cartBody.prepend(str);
                                // cartBody.prepend("<tr><th scope=\"row\">" + i + "</th> <th> <a href='" + value.url + "'>" + value.name + "</a></th> <th>" + value.price + "</th><th>" + newHRB.html() + "</th>  </tr>")
                                i = i - 1
                            })
                            cartBody.find(".cart-subtotal").text(data.subtotal)
                            cartBody.find(".cart-total").text(data.total)
                        } else {
                            window.location.href = '/cart/'
                            // window.location.href = currentUrl
                        }

                    },
                    error: function (err) {
                        console.log("errrr")
                        console.log(err)
                    }
                })
            }

        })
    })