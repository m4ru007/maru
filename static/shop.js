// Ajoutez ce code dans un fichier shop.js dans votre dossier static
// puis importez-le dans votre boutique.html

// Fonction pour vérifier si l'utilisateur a assez de points
function checkBalance(itemPrice, userBalance) {
    return userBalance >= itemPrice;
}

// Fonction pour afficher une animation lors de l'achat
function purchaseAnimation(itemElement, itemPrice, userBalance) {
    // Créer l'overlay pour l'animation
    const overlay = document.createElement('div');
    overlay.className = 'purchase-overlay';
    document.body.appendChild(overlay);
    
    // Créer la boîte de dialogue
    const dialogBox = document.createElement('div');
    dialogBox.className = 'purchase-dialog';
    
    // Récupérer les informations de l'item
    const itemName = itemElement.querySelector('h2').textContent;
    const itemImage = itemElement.querySelector('img').src;
    
    // Vérifier si l'utilisateur a assez de points
    const hasEnoughPoints = checkBalance(itemPrice, userBalance);
    
    // Construire le contenu de la boîte de dialogue
    dialogBox.innerHTML = `
        <div class="dialog-header">
            <h3>Confirmation d'achat</h3>
            <button class="close-dialog">×</button>
        </div>
        <div class="dialog-content">
            <div class="item-preview">
                <img src="${itemImage}" alt="${itemName}" class="preview-image">
                <h4>${itemName}</h4>
                <p class="item-price">${itemPrice} points</p>
            </div>
            <div class="balance-info ${hasEnoughPoints ? 'sufficient' : 'insufficient'}">
                ${hasEnoughPoints ? 
                    `<p><i class="fas fa-check-circle"></i> Vous avez assez de points</p>
                     <p>Solde actuel: ${userBalance} points</p>
                     <p>Solde après achat: ${userBalance - itemPrice} points</p>` 
                    : 
                    `<p><i class="fas fa-times-circle"></i> Points insuffisants</p>
                     <p>Solde actuel: ${userBalance} points</p>
                     <p>Il vous manque ${itemPrice - userBalance} points</p>
                     <a href="/achat_points" class="buy-more-btn">Acheter des points</a>`
                }
            </div>
        </div>
        <div class="dialog-footer">
            ${hasEnoughPoints ? 
                `<button class="confirm-purchase">Confirmer l'achat</button>` 
                : 
                `<button class="cancel-purchase">Annuler</button>`
            }
        </div>
    `;
    
    overlay.appendChild(dialogBox);
    
    // Animation d'entrée
    setTimeout(() => {
        overlay.classList.add('active');
        dialogBox.classList.add('active');
    }, 10);
    
    // Gérer les clics sur les boutons
    const closeButton = dialogBox.querySelector('.close-dialog');
    const cancelButton = dialogBox.querySelector('.cancel-purchase');
    const confirmButton = dialogBox.querySelector('.confirm-purchase');
    
    // Fonction pour fermer la boîte de dialogue
    const closeDialog = () => {
        overlay.classList.remove('active');
        dialogBox.classList.remove('active');
        setTimeout(() => {
            overlay.remove();
        }, 300);
    };
    
    // Ajouter les écouteurs d'événements
    if (closeButton) closeButton.addEventListener('click', closeDialog);
    if (cancelButton) cancelButton.addEventListener('click', closeDialog);
    
    if (confirmButton) {
        confirmButton.addEventListener('click', () => {
            // Remplacer le contenu par une animation de chargement
            dialogBox.innerHTML = `
                <div class="loading-animation">
                    <div class="spinner"></div>
                    <p>Traitement de votre achat...</p>
                </div>
            `;
            
            // Simuler le traitement (remplacez ceci par votre logique d'achat réelle)
            setTimeout(() => {
                // Afficher confirmation de succès
                dialogBox.innerHTML = `
                    <div class="success-message">
                        <i class="fas fa-check-circle success-icon"></i>
                        <h3>Achat réussi !</h3>
                        <p>${itemName} a été ajouté à votre inventaire</p>
                        <button class="ok-button">OK</button>
                    </div>
                `;
                
                // Ajouter écouteur sur le bouton OK
                const okButton = dialogBox.querySelector('.ok-button');
                if (okButton) okButton.addEventListener('click', () => {
                    closeDialog();
                    // Soumettre le formulaire pour compléter l'achat côté serveur
                    itemElement.querySelector('form').submit();
                });
                
            }, 1500);
        });
    }
}

// Fonction pour initialiser les boutons d'achat
function initPurchaseButtons(userBalance) {
    const items = document.querySelectorAll('.item');
    
    items.forEach(item => {
        const buyButton = item.querySelector('.buy-button');
        const priceText = item.querySelector('p').textContent;
        const price = parseInt(priceText.match(/\d+/)[0]);
        
        // Remplacer le comportement du bouton
        buyButton.addEventListener('click', (e) => {
            e.preventDefault();
            purchaseAnimation(item, price, userBalance);
        });
    });
}

// Charger le solde de l'utilisateur depuis le serveur
function loadUserBalance() {
    // Dans un environnement réel, vous récupéreriez cette valeur du serveur
    // Par exemple via une requête fetch ou depuis une variable Flask
    
    // Pour l'exemple, nous utilisons une valeur statique
    // Remplacez ceci par le vrai solde de l'utilisateur
    const userBalance = {{ user_points if user_points is defined else 500 }};
    
    // Afficher le solde dans l'interface
    const balanceDisplay = document.createElement('div');
    balanceDisplay.className = 'balance-display';
    balanceDisplay.innerHTML = `<p>Votre solde: <span>${userBalance}</span> points</p>`;
    
    const header = document.querySelector('.header');
    header.appendChild(balanceDisplay);
    
    return userBalance;
}

// Initialiser lorsque le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    const userBalance = loadUserBalance();
    initPurchaseButtons(userBalance);
});