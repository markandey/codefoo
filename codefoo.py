import sublime
import sublime_plugin
import urllib
import urllib2
import threading
import re
import json

class CodefooCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sels = self.view.sel()
        threads = []
        for sel in sels:
            string = self.view.substr(sel)
            string = self.view.substr(sel)
            thread = FooIOThread(sel, string,100)
            threads.append(thread)
            thread.start()
            self.handle_threads(edit, threads)
    def injectResult(self,edit,sel,result):
        try:
            dump=result["query"]["results"]
            resultDump=dump["results"]
            code=resultDump["code"]
            if code == 'Sorry! service is down':
                raise;
            try:
                bossresponse=resultDump["info"]["bossresponse"]["web"]["results"]["result"];
                abstract=bossresponse["abstract"]['content'];
                clickurl=bossresponse["clickurl"];
            except:
                bossresponse=""
                abstract=""
                clickurl=""
        except:
            self.view.set_status('foo',"Sorry!!!!! API rate limit Exceeded ..., retry again!, We will fix soon.");
            return 

        output=""
        output=output+'\n#################################################\n';
        output=output+"Description: "+abstract;
        output=output+"\nURL: "+clickurl;
        output=output+'\n#################################################\n';
        output=output+code;
        output=output+'\n#################################################\n';
        self.view.replace(edit,sel,output);
        self.view.run_command('toggle_comment') 

    def handle_threads(self, edit, threads,i=0):
            next_threads = []
            for thread in threads:
                if thread.is_alive():
                    next_threads.append(thread)
                    continue
                if thread.result == False:
                    continue
                self.injectResult(edit, thread.sel, thread.result);
            
            threads = next_threads
            if len(threads):
                before = i % 8
                after = (7) - before
                if not after:
                    dir = -1
                if not before:
                    dir = 1
                i += dir
                self.view.set_status('foo', 'Foo [%s=%s]' % \
                    (' ' * before, ' ' * after))
                sublime.set_timeout(lambda: self.handle_threads(edit, threads), 100)
                return

            self.view.end_edit(edit)

            #self.view.erase_status('foo')
            selections = len(self.view.sel())
            sublime.status_message('Foo  loaded for %s selection%s' %(selections, '' if selections == 1 else 's'))

class FooIOThread(threading.Thread):
    def __init__(self, sel, query, timeout):
        self.sel = sel
        self.query = query
        self.timeout = timeout
        self.result = None
        threading.Thread.__init__(self)

    def run(self):
        try:
            data = urllib.urlencode({'query': self.query})
            request = urllib2.Request("http://query.yahooapis.com/v1/public/yql?q=use%20%22store%3A%2F%2FpLutAvbH8CPrXJCnluWppu%22%20as%20foo%3B%20select%20*%20from%20foo%20where%20q%3D'"+urllib.quote(self.query, '')+"'%3B&format=json&&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys", data,
                headers={"User-Agent": "Foo"})
            http_file = urllib2.urlopen(request, timeout=self.timeout)
            self.result = json.loads(http_file.read());
            print self.result;
            return
        except (urllib2.HTTPError) as (e):
            err = '%s: HTTP error %s contacting API' % (__name__, str(e.code))
        except (urllib2.URLError) as (e):
            err = '%s: URL error %s contacting API' % (__name__, str(e.reason))
        sublime.error_message(err)
        self.result = False
