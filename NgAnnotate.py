import sublime, sublime_plugin, re

class NgAnnotateCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view

        # for region in view.sel():
        region = view.sel()[0]
        originalStart = region.begin()
        originalEnd = region.end()

        def _revertSelection(s1, s2):
            view.sel().clear()
            view.sel().add(sublime.Region(s1, s2))

        def _moveToFunction():
            s = view.sel()[0].begin()
            while s >= 0 and view.substr(sublime.Region(s, s + 8)) != 'function':
                s -= 1

            if view.substr(sublime.Region(s, s + 8)) != 'function':
                return False

            _revertSelection(s + 1, s + 1)
            return True

        if view.substr(view.word(view.sel()[0])) != 'function':
            if _moveToFunction() == False:
                _revertSelection(originalStart, originalEnd)
                return

        def _annotate(s1, s2):
            str = view.substr(sublime.Region(s1, s2))
            match = re.match(r'function\s*[^\(]*?\s*\(([^\)]+)', str, re.M)

            if match != None:
                args = match.group(1)
                r = re.sub(r'([^,\s]+)', '\'\g<1>\'', args)
                res = '[' + r + ', ' + str + ']'
                view.replace(edit, sublime.Region(s1, s2), res)
                return r
            return None

        def _addNewAnnotation():
            _revertSelection(originalStart, originalEnd)
            _moveToFunction()
            s0 = view.word(view.sel()[0]).begin()
            s1 = originalStart

            while s1 < view.size() - 1 and view.substr(sublime.Region(s1, s1 + 1)) != '{':
                s1 = s1 + 1;

            if view.substr(sublime.Region(s1, s1 + 1)) != '{':
                return

            s1 = s1 + 1;

            _revertSelection(s1, s1)

            view.run_command('expand_selection', {'to': 'brackets'})

            region = view.sel()[0];
            # string = view.substr(sublime.Region(0, view.size()))
            start = region.begin()
            end = region.end()
            end = end + 1
            start = start - 1

            annotation = _annotate(s0, end)
            added = 0
            if annotation != None:
                added = len(annotation) + 3

            _revertSelection(originalStart + added, originalEnd + added)

        view.run_command('expand_selection', {'to': 'brackets'})
        view.run_command('expand_selection', {'to': 'brackets'})

        alreadyAnnotated = view.substr(view.sel()[0])
        match = re.match(r'(\[[^\{]*?)function[\s\S]*?\]$', alreadyAnnotated)
        if (match != None):
            r = re.sub(r'\[[^\{]*?(function[\s\S]*?)\]$', '\g<1>', alreadyAnnotated)
            view.replace(edit, view.sel()[0], r)
            originalStart -= len(match.group(1))
            originalEnd -= len(match.group(1))
            _addNewAnnotation()
        else:
            _addNewAnnotation()
