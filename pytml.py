class RenderError(Exception):
    pass


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
            marks[detected_codes-1] = marks[detected_codes -1][0], index - do_not_detects
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

def render_from_string(string:str, context=None) -> str:
    if context is None:
        context = {}
    code, marks = order_by_syntax(string, "{", "}")
    new_code = str(code)
    for mark in marks:
        if len(code[mark[0]+1:mark[1]].strip().split(";", 2)) < 2:
            raise SyntaxError(f"invalid syntax in {code[mark[0]:mark[1]+1].strip()}")
        part = code[mark[0]+1:mark[1]]
        script = part.strip().split(";", 2)[0].strip()
        value = part.strip().split(";", 2)[1].strip()
        try:
            html_value = part.strip().split(";", 2)[2].strip()
        except IndexError:
            html_value = ""
        returned = eval(f"_{script}('{value[1:-1]}', '{html_value[1:-1]}', {context})")
        if returned is None:
            returned = ""
        new_code = new_code.replace(code[mark[0]:mark[1]+1], returned)
    return new_code

def render(filename:str, context=None) -> str:
    if context is None:
        context = {}

    with open(filename, encoding="utf-8") as f:
        string = f.read()
    return render_from_string(string, context)

def _if(statement:str, value:str, context:dict) -> str:
    for var in context.items():
        exec(f"{var[0]} = {var[1]}")
    if eval(statement):
        return render_from_string(value, context)
    else:
        return ""

def _for(statement:str, value:str, context:dict) -> str:
    send = ""
    for var in context.items():
        exec(f"{var[0]} = {var[1]}")
    if len(statement.split(" ")) != 3:
        raise SyntaxError(f"invalid syntax in for in {statement}")
    exec(f"""for i in {statement.split(' ')[2]}:\n    context['{statement.split(' ')[0]}'] = i\n    send += {render_from_string(value)}""")
    return send

def _cal(statement:str, value:str, context:dict) -> str:
    for var in context.items():
        exec(f"{var[0]} = {var[1]}")
    return str(eval(statement))
