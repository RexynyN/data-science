const scrapper = async () => {
    // Range for the for loop (lol)
    function range (stop){
        let start = 0;
        return Array.from({ length: (stop - start) },(value, index) => start + index);
    }
    // A Thread.sleep lookalike
    async function sleep(msec){
        return new Promise(resolve => setTimeout(resolve, msec));
    }
    // Number of images to grab
    const numImages = 10;

    // Clicks on the first image in the grid to open the side menu
    document.getElementsByClassName("FRuiCf islib nfEiy")[0].click();
    await sleep(1000)

    // Clicks and clicks on the next image grabbing the source for it
    const nextButton = document.querySelector('[jsaction="trigger.g9z3Gc"][class="wvfN0b"][jsname="OCpkoe"]')
    let urls = []
    for(let i of range(numImages)){
        let img = document.querySelector('[jsaction="VQAsE"][class="sFlh5c pT0Scc iPVvYb"]')
        urls.push(img.src);
        nextButton.click();
        await sleep(1000);
    }
    return urls;
}
await scrapper();