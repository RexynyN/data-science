// Fetch titles and prices
window.getData = () => {
    // Select all of the divs of the items to search through
    let items = document.querySelectorAll('[id^="itemInfo_"]');
    let data = [];
    let title, price, whole, fraction;

    for (item of items) {
        // Get the title from within the div
        title = item.querySelectorAll('[id^="itemName_"]')[0].title;

        // Do a whole ordeal to get price (ffs amazon, put it all in one span)
        try {
            whole = item.getElementsByClassName("a-price-whole")[0].innerText;      
            fraction = item.getElementsByClassName("a-price-fraction")[0].innerText;
        } catch (error) {
            whole = "-01,";
            fraction = "00";
        }

        price = whole + fraction;
        price = Number(price.replace(",", "."));

        // Push 
        data.push([title, price]);
    }

    console.log(data)

    return data;
}


// Pegar os titulos
window.getTitle = () => {
    let dates = document.querySelectorAll('[id^="itemName_"]');
    let titles = [];
    for (item of dates) {
        titles.push(item.title);
    }

    return titles;
}

// Pegar os preços
window.getPrices = () => {
    let whole = document.getElementsByClassName("a-price-whole");
    let fraction = document.getElementsByClassName("a-price-fraction");
    let prices = [];
    for (let i = 0; i < whole.length; i++) {
        let price = whole[i].innerText + fraction[i].innerText;
        price = price.replace(",", ".");
        prices.push(price);
    }
    
    return prices;
}

