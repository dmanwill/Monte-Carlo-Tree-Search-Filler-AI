import jester, karax/[karaxdsl, vdom], nimpy, strformat, strutils, sequtils, times
let sys = pyImport("sys")
discard sys.path.append("..") # get module from above
let board = pyImport("Board")
let mcts = pyImport("MCTS")
var game = board.Board()
var ai = "greedy"
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
      br()
      label(`for` = "ai"):
        text "Choose an AI:"
      select(id = "ai", name = "ai"):
        option(value = "greedy"):
          text "Greedy"
        if ai == "mcts":
          option(value = "mcts", selected = ""):
            text "Monte Carlo Tree Search"
        else:
          option(value = "mcts"):
            text "Monte Carlo Tree Search"

      br()
      input(type="submit", value="Reset Game")
proc render(): string =
  let vnode = buildHTML(tdiv):
    p: text &"Playing against {ai}"
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
    var aiMove: int
    if ai == "greedy":
      aiMove = game.greedy_move(2).to(int)
    elif ai == "mcts":
      var time = now()
      var mcts = mcts.MCTS(game, 2, exploration_parameter = 5, intelligence_parameter = 0.5)
      aiMove = mcts.select_move(200).to(int)
    discard game.update_board(2, aiMove)
    redirect "/"
  get "/reset":
    var width = @"width".parseInt
    var height = @"height".parseInt
    ai = @"ai"
    game = board.Board(size=(height, width))
    redirect "/"
