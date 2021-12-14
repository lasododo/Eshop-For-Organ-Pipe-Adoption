$(document).ready(function () {

    var stripeFormModule = $(".stripe-payment-form")
    var stripeTemplate = $.templates("#stripeTemplate")
    var stripeToken = stripeFormModule.attr("data-token")
    var stripeNextUrl = stripeFormModule.attr("data-next-url")
    var stripeModuleBtnTitle = stripeFormModule.attr("data-btn-title") || "Submit it!"
    var stripeTemplateDataCont = {
        publish_key: stripeToken,
        next_url: stripeNextUrl,
        btn_title: stripeModuleBtnTitle
    }

    var stripeTempleHTML = stripeTemplate.render(
        stripeTemplateDataCont
    )

    stripeFormModule.html(stripeTempleHTML)


    var paymentForm = $(".payment-form")

    if (paymentForm.length > 1) {
        paymentForm.css('display', 'none')
    } else if (paymentForm.length == 1) {
        var pubKey = paymentForm.attr('data-token')

        var nextUrl = paymentForm.attr('data-next-url')

        // Create a Stripe client
        var stripe = Stripe(pubKey);

        // Create an instance of Elements
        var elements = stripe.elements();

        console.log(elements.length)

        // Custom styling can be passed to options when creating an Element.
        // (Note that this demo uses a wider set of styles than the guide below.)
        var style = {
            base: {
                color: '#32325d',
                lineHeight: '24px',
                fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
                fontSmoothing: 'antialiased',
                fontSize: '16px',
                '::placeholder': {
                    color: '#aab7c4'
                }
            },
            invalid: {
                color: '#fa755a',
                iconColor: '#fa755a'
            }
        };

        // Create an instance of the card Element
        var card = elements.create('card', {hidePostalCode: true, style: style});

        // Add an instance of the card Element into the `card-element` <div>
        card.mount('#card-element');

        // Handle real-time validation errors from the card Element.
        card.addEventListener('change', function (event) {
            var displayError = document.getElementById('card-errors');
            if (event.error) {
                displayError.textContent = event.error.message;
            } else {
                displayError.textContent = '';
            }
        });

        // Handle form submission
        var form = document.getElementById('payment-form');
        form.addEventListener('submit', function (event) {
            event.preventDefault();

            stripe.createToken(card).then(function (result) {
                if (result.error) {
                    // Inform the user if there was an error
                    var errorElement = document.getElementById('card-errors');
                    errorElement.textContent = result.error.message;
                } else {
                    // Send the token to your server
                    stripeTokenHandler(result.token);
                }
            });
        });
    }

    function stripeTokenHandler(token) {
        console.log(token.id)

        var paymentMethodEndpoint = '/billing/payment/create/'
        var data = {
            'token': token.id
        }

        $.ajax({
            data: data,
            url: paymentMethodEndpoint,
            method: "POST",
            success: function (data) {
                console.log(data)

                card.clear()

                var success = data.message || "Successfully added ... "

                if (nextUrl) {
                    success = success + " redirecting ... "
                }

                if ($.alert) {
                    $.alert(success)
                } else {
                    alert(success)
                }

                if (nextUrl) {
                    setTimeout(function () {
                        window.location.href = nextUrl
                    }, 1000)
                }
            },
            error: function (error) {
                console.log(error)
            }
        })
    }


})
