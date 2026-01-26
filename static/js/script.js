// Detectar cuando se cierra la pestaña
window.addEventListener('beforeunload', function() {
    navigator.sendBeacon('/ping');
});

// Mantener viva la conexión cada 20 segundos
setInterval(function() {
    fetch('/ping').catch(err => console.log('Servidor cerrado'));
}, 20000);

// Toggle entre vistas
function toggleView(view) {
    const comparisonView = document.getElementById('comparison-view');
    const listView = document.getElementById('list-view');
    const comparisonBtn = document.getElementById('comparison-btn');
    const listBtn = document.getElementById('list-btn');

    if (view === 'comparison') {
        comparisonView.classList.add('active');
        listView.classList.remove('active');
        comparisonBtn.classList.add('active');
        listBtn.classList.remove('active');
    } else {
        comparisonView.classList.remove('active');
        listView.classList.add('active');
        comparisonBtn.classList.remove('active');
        listBtn.classList.add('active');
    }
}

// Carrito de compras
let cart = JSON.parse(sessionStorage.getItem('cart')) || [];

function updateCartDisplay() {
    const cartItems = document.getElementById('cart-items');
    const cartTotal = document.getElementById('cart-total');
    const cartCount = document.getElementById('cart-count');
    
    cartItems.innerHTML = '';
    let total = 0;
    let count = 0;
    
    // Agrupar por fuente
    const groupedCart = {};
    cart.forEach(item => {
        if (!groupedCart[item.fuente]) {
            groupedCart[item.fuente] = [];
        }
        groupedCart[item.fuente].push(item);
        total += item.subtotal;
        count += item.cantidad;
    });
    
    for (const [fuente, items] of Object.entries(groupedCart)) {
        const fuenteDiv = document.createElement('div');
        fuenteDiv.className = 'cart-provider';
        fuenteDiv.innerHTML = `<h4>${fuente}</h4>`;
        
        items.forEach((item, index) => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'cart-item';
            itemDiv.innerHTML = `
                <div class="cart-item-info">
                    <span class="cart-item-name">${item.nombre}</span>
                    <div class="cart-item-details">
                        <span>Proveedor: ${item.proveedor}</span>
                        <span>Cantidad: 
                            <button class="qty-btn-small" onclick="changeCartQuantity('${fuente}', ${index}, -1)">-</button>
                            <input type="number" class="qty-input-small" value="${item.cantidad}" min="1" onchange="updateCartSubtotal('${fuente}', ${index}, this.value)">
                            <button class="qty-btn-small" onclick="changeCartQuantity('${fuente}', ${index}, 1)">+</button>
                        </span>
                        <span>Precio: S/ ${item.precio.toFixed(2)}</span>
                        <span>Subtotal: S/ ${item.subtotal.toFixed(2)}</span>
                    </div>
                </div>
                <button class="remove-btn" onclick="removeFromCart('${fuente}', ${index})">🗑️</button>
            `;
            fuenteDiv.appendChild(itemDiv);
        });
        
        cartItems.appendChild(fuenteDiv);
    }
    
    cartTotal.textContent = total.toFixed(2);
    cartCount.textContent = count;
    sessionStorage.setItem('cart', JSON.stringify(cart));
}

function addToCartFromButton(button) {
    const nombre = button.dataset.nombre;
    const proveedor = button.dataset.proveedor;
    const precio = parseFloat(button.dataset.precio);
    const fuente = button.dataset.fuente;
    addToCart(nombre, proveedor, precio, fuente, button);
}

function addToCart(nombre, proveedor, precio, fuente, button) {
    const qtyInput = button.parentElement.querySelector('.qty-input');
    const cantidad = parseInt(qtyInput.value);
    const subtotal = precio * cantidad;
    
    // Verificar si ya existe el producto
    const existingIndex = cart.findIndex(item => item.nombre === nombre && item.proveedor === proveedor && item.fuente === fuente);
    
    if (existingIndex >= 0) {
        cart[existingIndex].cantidad += cantidad;
        cart[existingIndex].subtotal = cart[existingIndex].precio * cart[existingIndex].cantidad;
    } else {
        cart.push({
            nombre: nombre,
            proveedor: proveedor,
            precio: precio,
            fuente: fuente,
            cantidad: cantidad,
            subtotal: subtotal
        });
    }
    
    updateCartDisplay();
    // Animación de feedback
    button.textContent = '✅ Agregado';
    setTimeout(() => {
        button.innerHTML = '🛒 Agregar al Carrito';
    }, 1000);
}

function removeFromCart(fuente, index) {
    const fuenteItems = cart.filter(item => item.fuente === fuente);
    cart.splice(cart.indexOf(fuenteItems[index]), 1);
    updateCartDisplay();
}

function changeCartQuantity(fuente, index, delta) {
    const fuenteItems = cart.filter(item => item.fuente === fuente);
    const item = fuenteItems[index];
    item.cantidad = Math.max(1, item.cantidad + delta);
    item.subtotal = item.precio * item.cantidad;
    updateCartDisplay();
}

function updateCartSubtotal(fuente, index, newQty) {
    const fuenteItems = cart.filter(item => item.fuente === fuente);
    const item = fuenteItems[index];
    item.cantidad = Math.max(1, parseInt(newQty) || 1);
    item.subtotal = item.precio * item.cantidad;
    updateCartDisplay();
}

function changeQuantity(button, delta) {
    const input = button.parentElement.querySelector('.qty-input');
    const newValue = Math.max(1, parseInt(input.value) + delta);
    input.value = newValue;
}

function updateSubtotal(input) {
    // Opcional: actualizar subtotal en tiempo real si se muestra
}

function toggleCart() {
    const panel = document.getElementById('cart-panel');
    panel.classList.toggle('active');
}

function exportToWord() {
    if (cart.length === 0) {
        alert('El carrito está vacío');
        return;
    }
    
    fetch('/export_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(cart)
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            throw new Error('Error al exportar');
        }
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'lista_compras.docx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al exportar el documento');
    });
}

// Inicializar carrito al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    updateCartDisplay();
});