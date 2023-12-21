/*  ---------------------------------------------------
    Template Name: Loja Template
    Description:  Loja eCommerce  HTML Template
    Author: Colorlib
    Author URI: https://colorlib.com
    Version: 1.0
    Created: Colorlib
---------------------------------------------------------  */

'use strict';

(function ($) {

    /*------------------
        Preloader
    --------------------*/
    $(window).on('load', function () {
        $(".loader").fadeOut();
        $("#preloder").delay(200).fadeOut("slow");
        var fixedTopElement = document.querySelector('.fixed-top'); // Seletor do elemento fixo
  var mainContent = document.querySelector('.main-content'); // Seletor do elemento principal

  // Verifica se o elemento fixo existe
  if (fixedTopElement) {
    var fixedTopHeight = fixedTopElement.offsetHeight; // Obtém a altura do elemento fixo
    console.log(fixedTopHeight);

    // Ajusta o padding-top do elemento principal adicionando 5% da altura do elemento fixo
    mainContent.style.paddingTop = (fixedTopHeight + fixedTopHeight * 0.05) + 'px';
    console.log(mainContent.style.paddingTop);
  }
        /*------------------
            Gallery filter
        --------------------*/
        $('.product__controls li').on('click', function () {
            $('.product__controls li').removeClass('active');
            $(this).addClass('active');
            var filtro = this.dataset.filter;
            owl_feature.owlcarousel2_filter( filtro );
            owl_feature.trigger('destroy.owl.carousel');
            owl_feature.owlCarousel({
        loop: false,
        margin: 0,
        items: 4,
        dots: false,
        nav: true,
        navText: ["<span class='fa fa-angle-left'><span/>", "<span class='fa fa-angle-right'><span/>"],
        animateOut: 'fadeOut',
        animateIn: 'fadeIn',
        smartSpeed: 1200,
        autoHeight: false,
        autoplay: false,
        responsive: {

            0: {
                items: 1,
            },

            480: {
                items: 2,
            },

            768: {
                items: 3,
            },

            992: {
                items: 4
            }
        }


    });

        });

//        if ($('.featured__filter').length > 0) {
//            console.log("FUNCIONANDO")
//            var containerEl = document.querySelector('.featured__filter');
//            var mixer = mixitup(containerEl);
//            $('.featured__slider').trigger('resize.owl.carousel');
////            owl_feature.owlCarousel();
//        }

    });

    /*------------------
        Background Set
    --------------------*/
    $('.set-bg').each(function () {
        var bg = $(this).data('setbg');
        $(this).css('background-image', 'url(' + bg + ')');
    });

    $('.set-bg-cover').each(function () {
    var bg = $(this).data('setbg');
    $(this).css('background-image', 'url(' + bg + ')');
});

    //Humberger Menu
    $(".humberger__open").on('click', function () {
        $(".humberger__menu__wrapper").addClass("show__humberger__menu__wrapper");
        $(".humberger__menu__overlay").addClass("active");
        $("body").addClass("over_hid");
    });

    $(".humberger__menu__overlay").on('click', function () {
        $(".humberger__menu__wrapper").removeClass("show__humberger__menu__wrapper");
        $(".humberger__menu__overlay").removeClass("active");
        $("body").removeClass("over_hid");
    });

    /*------------------
		Navigation
	--------------------*/
    $(".mobile-menu").slicknav({
        prependTo: '#mobile-menu-wrap',
        allowParentLinks: true
    });

    /*-----------------------
        Categories Slider
    ------------------------*/
    $(".categories__slider").owlCarousel({
        loop: true,
        margin: 0,
        items: 2,
        dots: false,
        nav: true,
        navText: ["<span class='fa fa-angle-left'><span/>", "<span class='fa fa-angle-right'><span/>"],
        animateOut: 'fadeOut',
        animateIn: 'fadeIn',
        smartSpeed: 1200,
        autoHeight: false,
        autoplay: true,
        responsive: {

            0: {
                items: 1,
            },

            480: {
                items: 2,
            },

            768: {
                items: 3,
            },

            992: {
                items: 4,
            }
        }
    });


    $('.hero__categories__all').on('click', function(){
        $('.hero__categories ul').slideToggle(400);
    });





        /*-----------------------
        Featured Slider
    ------------------------*/
    let owl_feature = $(".product__slider").owlCarousel({
        loop: false,
        margin: 0,
        items: 4,
        dots: true,
        nav: false,
        navText: ["<span class='fa fa-angle-left'><span/>", "<span class='fa fa-angle-right'><span/>"],
        animateOut: 'fadeOut',
        animateIn: 'fadeIn',
        smartSpeed: 1200,
        autoHeight: false,
        autoplay: false,
        responsive: {

            0: {
                items: 1,
            },

            480: {
                items: 2,
            },

            768: {
                items: 3,
            },

            992: {
                items: 4,
            }
        }


    });


     /*-----------------------
        Banners Secundarios Slider
    ------------------------*/
    $(".secundary_banner__slider").owlCarousel({
        loop: false,
        margin: 2,
        items: 2,
        dots: false,
        nav: false,
        navText: ["<span class='fa fa-angle-left'><span/>", "<span class='fa fa-angle-right'><span/>"],
        smartSpeed: 1200,
        autoHeight: false,
        autoplay: true,
        responsive: {

            0: {
                items: 1,
            },

            480: {
                items: 1,
            },

            768: {
                items: 2,
            },

            992: {
                items: 2,
            }
        }
    });




    /*--------------------------
        Latest Product Slider
    ----------------------------*/
    $(".latest-product__slider").owlCarousel({
        loop: true,
        margin: 0,
        items: 1,
        dots: false,
        nav: true,
        navText: ["<span class='fa fa-angle-left'><span/>", "<span class='fa fa-angle-right'><span/>"],
        smartSpeed: 1200,
        autoHeight: false,
        autoplay: true
    });

    /*-----------------------------
        Product Discount Slider
    -------------------------------*/
    $(".product__discount__slider").owlCarousel({
        loop: false,
        margin: 0,
        items: 3,
        dots: true,
        smartSpeed: 1200,
        autoHeight: false,
        autoplay: false,
        responsive: {

            320: {
                items: 1,
            },

            480: {
                items: 2,
            },

            768: {
                items: 3,
            },

            992: {
                items: 4,
            }
        }
    });

    /*---------------------------------
        Product Details Pic Slider
    ----------------------------------*/
    $(".product__details__pic__slider").owlCarousel({
        loop: false,
        margin: 20,
        items: 4,
        dots: true,
        smartSpeed: 1200,
        autoHeight: false,
        autoplay: false
    });






 /*-----------------------
		List Product Changer
	------------------------ */
    var listaToggle = document.getElementById('Lista_toggle');
    if (listaToggle) {
    listaToggle.addEventListener('click', function() {
        var container = document.querySelector('.product-container');
        if (container) {
            container.classList.toggle('product-list-view');
            listaToggle.classList.toggle('icon_ul');
            listaToggle.classList.toggle('icon_grid-2x2');
        }
    });
}
    /*-----------------------
		Price Range Slider
	------------------------ */
    var rangeSlider = $(".price-range"),
        minamount = $("#minamount"),
        maxamount = $("#maxamount"),
        minPrice = rangeSlider.data('min'),
        maxPrice = rangeSlider.data('max');
    rangeSlider.slider({
        range: true,
        min: minPrice,
        max: maxPrice,
        values: [minPrice, maxPrice],
        slide: function (event, ui) {
            minamount.val('$' + ui.values[0]);
            maxamount.val('$' + ui.values[1]);
        }
    });
    minamount.val('$' + rangeSlider.slider("values", 0));
    maxamount.val('$' + rangeSlider.slider("values", 1));

    /*--------------------------
        Select
    ----------------------------*/
   // $("select").niceSelect();

    /*------------------
		Single Product
	--------------------*/
    $('.product__details__pic__slider img').on('click', function () {

        var imgurl = $(this).data('imgbigurl');
        var bigImg = $('.product__details__pic__item--large').attr('src');
        if (imgurl != bigImg) {
            $('.product__details__pic__item--large').attr({
                src: imgurl
            });
        }
    });





//ALERTBOX




    /*-------------------
		Quantity change
	--------------------- */
    var proQty = $('.pro-qty');
    proQty.prepend('<span class="dec qtybtn">-</span>');
    proQty.append('<span class="inc qtybtn">+</span>');
    proQty.on('click', '.qtybtn', function () {
        var $button = $(this);
        var oldValue = $button.parent().find('input').val();
        if ($button.hasClass('inc')) {
            var newVal = parseFloat(oldValue) + 1;
        } else {
            // Don't allow decrementing below zero
            if (oldValue > 0) {
                var newVal = parseFloat(oldValue) - 1;
            } else {
                newVal = 0;
            }
        }
        $button.parent().find('input').val(newVal);
    });

})(jQuery);


/*-----------------------
		opcoes quantidade e variaveis
	------------------------ */
let openOptions = null;

function showOptions(button) {
    // Encontrar a div pai mais próxima com a classe 'product__item'
    if (openOptions) {
        openOptions.style.display = 'none';
    }
    var parentDiv = button.closest('.product__item');

    if (parentDiv) {
        // Encontrar a div de opções dentro desta div pai
        var optionsDiv = parentDiv.querySelector('.product-options');

        if (optionsDiv) {
            // Exibir as opções do produto
            optionsDiv.style.display = 'flex';
            selecionarPrimeiraOpcao(optionsDiv);
            openOptions = optionsDiv;
        }
    }
}





function selecionarPrimeiraOpcao(parentDiv) {
    console.log('Funcionando');
    var select = parentDiv.querySelector('select');
    console.log('select',select);
    if (select && select.options.length > 0) {
        console.log(select.options.length);
        select.selectedIndex = 0;
        updatePrice(select)
    }
}


document.addEventListener('click', function(event) {
    if (openOptions && !openOptions.contains(event.target) && !event.target.closest('.product__item')) {
        openOptions.style.display = 'none';
        openOptions = null; // Reseta a referência após o fechamento
    }
});

// Fechar as opções
function closeOptions(button) {
    let options = button.closest('.product-options');
    options.style.display = 'none';
    openOptions = null; // Reseta a referência quando o botão de fechar é clicado
}

//FAVORITE
function favorite(button) {
    var produto_id = button.getAttribute('data-product-id');
    fetch('/favoritos/adicionar-favorito/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Obter o token CSRF
        },
        body: JSON.stringify({ 'produto_id': produto_id })
    })
    .then(response => response.json())
    .then(data => {

    if(data.success) {

      showSuccessAlert(data.message);
      $('#favoritos-container').load(location.href + ' #favoritos-container');
      document.getElementById('favorite-counter').textContent = data.favorite_counter;
      document.getElementById('favorite-counter-humberger').textContent = data.favorite_counter;
      // Alterna a cor do botão
            if (button.style.color === 'red') {
                button.style.color = ''; // Define para a cor original
            } else {
                button.style.color = 'red';
            }
    } else {

      showErrorAlert(data.error);
    }
  })

    .catch(error => {
        console.error('Erro:', error);

    }
    );
}


/*-----------------------
		Variation Price Changer
	------------------------ */
function updatePrice(selectElement) {
    console.log('Funcionando');
    var selectedOption = selectElement.options[selectElement.selectedIndex];
    var price = selectedOption.getAttribute('data-price');
    var produtoId = selectedOption.getAttribute('data-produto-id');
    var desconto = selectedOption.getAttribute('data-desconto');
    var variant_id = selectedOption.getAttribute('value');
    // Encontrar a div pai mais próxima com a classe 'product__item__price' e 'product__discount__percent'
    var parentDiv = selectElement.closest('.product__item');
    console.log('parentDiv',parentDiv,'price',price,'desconto',desconto,'variant_id',variant_id);
    if (parentDiv) {
        // Encontrar elementos de preço e desconto dentro desta div pai
        var priceElement = parentDiv.querySelector('.product__item__price');
        var discontElement = parentDiv.querySelector('.product__discount__percent');
        var variantplace = parentDiv.querySelector('.variationId');

        if (variant_id) {
            variantplace.value = variant_id;
        }
        if (priceElement) {
            priceElement.innerHTML = 'R$' + price;
        }
        if (discontElement) {
            discontElement.innerHTML = '-' + desconto + '%';

        }
    }
}


/*-----------------------
		Carrinho
	------------------------ */


// Adicionar item ao carrinho
function addToCart(formElement) {
  const productId = formElement.querySelector('.productId').value;
  const variationId = formElement.querySelector('.variationId').value || null; // Use null se o valor for vazio
  const quantity = formElement.querySelector('.quantity-input').value;
  console.log('productId',productId,'variationId',variationId,'quantity',quantity);
  const csrftoken = getCookie('csrftoken'); // Função para obter o token CSRF do cookie

  fetch('/carrinho/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,
    },
    body: JSON.stringify({
      'product_id': productId,
      'variant_id': variationId,
      'quantity': quantity
    })
  })
  .then(response => response.json())
  .then(data => {
    if(data.success) {
      console.log('Item adicionado ao carrinho.');
      updateCartSidebar(data.cart_sidebar);
      updateCartCounter(data.cart_counter_items)
      updateCartPage(data);
      showSuccessAlert(data.message);
    } else {
      console.error('Falha ao adicionar ao carrinho:', data.error);
      showErrorAlert(data.error);
    }
  })
  .catch(error => {
    console.error('Erro na requisição:', error);
  });
}


// Remover item do carrinho
function removeItem(itemId) {
  const csrftoken = getCookie('csrftoken'); // Função para obter o token CSRF do cookie

  fetch("/carrinho/", {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,
    },
    body: JSON.stringify({
      'item_id': itemId,
    })
  })
  .then(response => response.json())
  .then(data => {
    if(data.success) {
      console.log(data.message);
      updateCartSidebar(data.cart_sidebar);
      updateCartCounter(data.cart_counter_items);
      showSuccessAlert(data.message);
      updateCartPage(data);
      // Atualiza a tabela do carrinho se ela existir

    } else {
      console.error('Falha ao remover ao carrinho:', data.error);
      showErrorAlert(data.error);
    }
  })
  .catch(error => {
    console.error('Erro na requisição:', error);
  });
}

//Atuliza a pagina do carrinho
function updateCartPage(data) {
if(document.querySelector('.shoping__cart__table')) {
        document.querySelector('.shoping__cart__table').innerHTML = data.cart_partial;
      }
}


// Atualizar o contador do carrinho
function updateCartCounter(data) {


     document.getElementById('cart-counter').textContent = data.count;
     document.getElementById('cart-counter-humberger').textContent = data.count;

     let cartTotal = document.getElementById('cart-total');
        if (cartTotal) {
            cartTotal.textContent = data.total;
        }

    let cartTotalHumberger = document.getElementById('cart-total-humberger');
        if (cartTotalHumberger) {
            cartTotalHumberger.textContent = data.total;
        }
     console.log('contador carrinho')

 }

// Atualizar a barra lateral do carrinho
function updateCartSidebar(data) {
    const cartSidebar = document.getElementById('cart-sidebar');
    const isSidebarVisible = cartSidebar.classList.contains('visible');
    const sidebarContainer = document.getElementById('cart-sidebar-container');
            sidebarContainer.innerHTML = data;
            if (isSidebarVisible) {
                sidebarContainer.querySelector('#cart-sidebar').classList.add('visible');
                }
}



// Aumentar ou diminuir a quantidade do item no carrinho
function increaseQuantity(itemId) {
console.log(itemId)
    updateItemQuantity(itemId, 1);
}
// Aumentar ou diminuir a quantidade do item no carrinho
function decreaseQuantity(itemId) {
console.log(itemId)
    updateItemQuantity(itemId, -1);
}

// Atualizar a quantidade do item no carrinho
function updateItemQuantity(itemId, change) {
    fetch("/carrinho/", {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({

            item_id: itemId,
            change: change
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartSidebar(data.cart_sidebar);
            updateCartCounter(data.cart_counter_items);
            updateCartPage(data);
            showSuccessAlert(data.message);
        } else {
            showErrorAlert(data.error);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
    });
}






// Função para exibir/ocultar o carrinho
function toggleCartSidebar() {
  const cartSidebar = document.getElementById('cart-sidebar');
  cartSidebar.classList.toggle('visible');
}

// Função auxiliar para obter o valor do cookie CSRF
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}


function showAlert(message, type) {
  const alertBox = document.getElementById('alert-box');
  alertBox.textContent = message;
  alertBox.className = `alert-box alert-${type}`;
  alertBox.style.display = 'block';

  setTimeout(() => {
    alertBox.style.display = 'none';
  }, 3000); // O alerta desaparece após 3 segundos
}

function showSuccessAlert(message) {
  showAlert(message, 'success');
}

function showErrorAlert(message) {
  showAlert(message, 'error');
}


