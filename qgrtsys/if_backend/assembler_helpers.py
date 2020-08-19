import re


class Prog_line():

    def __init__(self, number=-1, content=''):
        self.number = number
        self.content = content

    def __repr__(self):
        return "prog_line(number={}, content={})".format(self.number,
                                                         self.content)

    def __str__(self):
        return "{}: {}".format(self.number, self.content)


def remove_comment(line):
    line = line.split('#', 1)[0]  # remove anything after '#' symbole
    line = line.strip(' \t\n\r')  # remove whitespace
    return line


def hack_meas_fmr_bug(prog_old_fn: str, prog_new_fn: str):
    prog_lines = []  # after removing comments.
    with open(prog_old_fn, 'r', encoding="utf-8") as prog_file:

        for line_number, line_content in enumerate(prog_file):
            line_content = remove_comment(line_content)

            line_content = line_content.lower()
            if (len(line_content) == 0):  # skip empty line and comment
                continue

            prog_lines.append(Prog_line(line_number + 1, line_content))

    start_meas_ln = 0
    found_qwait = False
    end_fmr_ln = 0
    prog_new = []

    for i, line in enumerate(prog_lines):
        if found_qwait is True:
            m = re.search('(?i)(qwait)\s+(\d+)', line.content)
            if m is not None:
                for j in range(start_meas_ln, i):
                    prog_new.append(prog_lines[j].content)

                start_meas_ln = i
                found_qwait = True
                continue

            m = re.search('(?i)(fmr)\s+r\d+\s*,\s*q\d+', line.content)
            if m is not None:
                end_fmr_ln = i
                new_qwaits = []
                new_qwaits.extend(
                    expand_qwait(prog_lines, start_meas_ln, end_fmr_ln))

                prog_new.extend(new_qwaits)

                found_qwait = False
                continue

        if found_qwait is False:
            m = re.search('(?i)(qwait)\s+(\d+)', line.content)
            if m is not None:
                start_meas_ln = i
                found_qwait = True
                continue

            prog_new.append(line.content)

    with open(prog_new_fn, 'w', encoding="utf-8") as prog_file:
        for line in prog_new:
            prog_file.write(line + '\n')

    return prog_new


def expand_qwait(prog_lines, start, end):
    # print('start:', start)
    # print('end:', end)
    m = re.search('(?i)(qwait)\s+(\d+)', prog_lines[start].content)
    assert(m is not None)
    old_wait_time = int(m.groups()[1])
    assert(old_wait_time > 4)
    new_qwaits = []
    new_qwaits.append("qwait {}".format(old_wait_time - 3))
    new_qwaits.append("qwait 1")
    new_qwaits.append("qwait 1")
    new_qwaits.append("qwait 1")

    for i in range(start + 1, end + 1):
        new_qwaits.append(prog_lines[i].content)

    # print("new_qwaits:", new_qwaits)

    return new_qwaits
