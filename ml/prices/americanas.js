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
    let dates = document.getElementsByClassName("src__Text-sc-154pg0p-0 product-card__Name-sc-rid09q-0 hmBRjq");
    let titles = [];
    for (item of dates) {
        let pipe = item.innerText.replace("Livro -", "")
        if(pipe.includes("+"))
            pipe = pipe.substring(0, pipe.indexOf("+"))
        titles.push(pipe.trim());
    }

    return titles;
}

// Pegar os preços
window.getPrices = () => {
    let data = document.getElementsByClassName("product-card__Price-sc-rid09q-4 EdfgT");
    let prices = [];
    for (item of data) {
        let price = item.innerText.replace(",", ".");
        price = price.replace("R$", "").trim();
        prices.push(Number(price));
    }
    
    return prices;
}

