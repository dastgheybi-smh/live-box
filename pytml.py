class RenderError(Exception):
    pass

preset = "./"

def set_render_preset(path: str = "/"):
    global preset
    preset = path

def order_by_syntax(text:str, syntax_start:str, syntax_end:str, do_not_detect="\\") -> tuple[str, list]:
    code = text.strip()
    index = 0
    open_codes = 0
    marks = []
    do_not_detects = 0
    detected_codes = 0
    insiders = 0
    while index < len(code):
        if code[index] == do_not_detect:
            index += 2
            do_not_detects += 1
            continue
        if code[index] == syntax_end and open_codes == 0:
            raise RenderError('syntax ended before starting')
        elif code[index] == syntax_end:
            if insiders > 0:
                index += 1
                insiders -= 1
                continue
            open_codes -= 1
            marks[detected_codes-1] = marks[detected_codes -1][0] + 1, index - do_not_detects
        elif code[index] == syntax_start:
            if open_codes > 0:
                index += 1
                insiders += 1
                continue
            open_codes += 1
            detected_codes += 1
            marks.append([index - do_not_detects, None])
        index += 1
    if open_codes != 0:
        raise RenderError('Open syntax(es) without closing detected')
    code = code.replace(do_not_detect + syntax_start, syntax_start)
    code = code.replace(do_not_detect + syntax_end, syntax_end)
    return code, marks


def order_by_syntax_double(text:str, syntax_start:str, syntax_end:str) -> list:

    code, marks = order_by_syntax(text, syntax_start[0], syntax_end[1])
    send = []

    for mark in marks:
        exe = code[mark[0]:mark[1]]
        code_, marks_ = order_by_syntax(exe, syntax_start[1], syntax_end[0])
        for mark_ in marks_:
            send.append(code_[mark_[0]: mark_[1]])

    return send

def render_from_string(string:str, context=None) -> str:
    if context is None:
        context = {}
    data = order_by_syntax_double(string, "{%", "$}")
    new_code = str(string)

    for mark in data:
        try:
            if not mark:
                continue
            if len(mark.strip().split(";", 2)) < 2:
                raise SyntaxError(f"invalid syntax in {mark.strip()}")
            part = mark
            script = part.strip().split(";", 2)[0].strip()
            value = part.strip().split(";", 2)[1].strip()
            try:
                html_value = part.strip().split(";", 2)[2].strip()
            except IndexError:
                html_value = ""
            returned = f"_{script.replace("\n", '').replace("\"", "\'")}(\"{value[1:-1].replace("\n", '').replace("\"", "\'")}\", \"{html_value[1:-1].replace("\n", '').replace("\"", "\'")}\", {context})"
            returned = eval(returned)
            if returned is None:
                returned = ""
            new_code = new_code.replace(f"{"{"}%{part}${"}"}", returned)
        except Exception as e:
            raise  e
    return new_code

def render(filename:str, context=None) -> str:
    if context is None:
        context = {}

    with open(preset+filename, encoding="utf-8") as f:
        string = f.read()
    return render_from_string(string, context)

def _if(statement:str, value:str, context:dict) -> str:
    for var in context.items():
        if type(var[1]) == str:
            val = f"'{var[1]}'"
        else:
            val = var[1]
        exec(f"{var[0]} = {val}")
    if eval(statement):
        return render_from_string(value, context)
    else:
        return ""

def _for(statement:str, value:str, context:dict) -> str:
    send = ""
    for var in context.items():
        if type(var[1]) == str:
            val = f"'{var[1]}'"
        else:
            val = var[1]
        exec(f"{var[0]} = {val}")
    if len(statement.split(" ")) != 3:
        raise SyntaxError(f"invalid syntax in for in {statement}")
    for i in eval(statement.split(' ')[2]):
        context[statement.split(' ')[0]] = i
        send += render_from_string(value, context)
        del context[statement.split(' ')[0]]

    return send

def _cal(statement:str, value:str, context:dict) -> str:
    for var in context.items():
        if type(var[1]) == str:
            val = f"'{var[1]}'"
        else:
            val = var[1]
        exec(f"{var[0]} = {val}")
    return str(eval(statement))

def _exec(statement:str, value:str, context:dict) -> None:
    for var in context.items():
        if type(var[1]) == str:
            val = f"'{var[1]}'"
        else:
            val = var[1]
        exec(f"{var[0]} = {val}")

    exec(statement)
