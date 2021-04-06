import jester, karax/[karaxdsl, vdom], nimpy, strformat, strutils, sequtils
let sys = pyImport("sys")
discard sys.path.append("..") # get module from above
let board = pyImport("Board")
var game = board.Board()
proc renderRow(row: PyObject): auto =
    buildHTML(tdiv(class="flex")):
        for color in row:
            tdiv(class = &"square color-{color}")
proc renderBoard(data: PyObject): VNode =
    buildHTML(tdiv(class = "dib")):
        for row in data:
            row.renderRow()
proc renderMoves(data: PyObject): VNode =
    buildHTML(tdiv(class="moves")):
        h3: text "Moves:"
        for move in data:
            a(href = &"/move/{move}"):
                tdiv(class = &"square color-{move}")
proc renderScore(data: PyObject): VNode =
    buildHTML(tdiv(class = "pv2")):
        bold: text "Your score: "
        span: text $data.get_score()[0]
        br()
        bold: text "AI score: "
        span: text $data.get_score()[1]
proc over(data: PyObject): bool =
    data.get_score()[0].to(int) + data.get_score()[1].to(int) == data.size[0].to(int) * data.size[1].to(int)
proc renderSettings(): VNode =
    buildHTML(tdiv):
        form(`method`="get", action="/reset"):
            input(type="number", value="8", placeholder="width", name="width")
            input(type="number", value="7", placeholder="height", name="height")
            input(type="submit", value="Reset Game")
proc render(): string =
    let vnode = buildHTML(tdiv):
        game.data.renderBoard
        if not game.over():
            game.legal_moves().renderMoves
        game.renderScore()
        renderSettings()
    return $vnode
var baseHTML = readFile("index.html")
routes:
    get "/":
        resp baseHTML % [render()]
    get "/move/@id":
        var id = parseInt(@"id")
        discard game.update_board(1, id)
        var greedy = game.greedy_move(2)
        discard game.update_board(2, greedy)
        redirect "/"
    get "/reset":
        var width = @"width".parseInt
        var height = @"height".parseInt
        game = board.Board(size=(height, width))
        redirect "/"
