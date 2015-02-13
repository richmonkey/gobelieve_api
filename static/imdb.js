function IMDB() {
    this.messages = {}
}

IMDB.prototype.saveMessage = function(uid, msg) {
    if (!this.messages[uid]) {
        this.messages[uid] = new Array()
    }
    this.messages[uid].push(msg)
}

IMDB.prototype.loadUserMessage = function(uid) {
    if (!this.messages[uid]) {
        return new Array();
    }
    return this.messages[uid];
}
