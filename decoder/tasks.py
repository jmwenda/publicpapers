from celery import Celery

import compose, decode, forms


celery = Celery('tasks', broker='redis://')


@celery.task
def decodeScan(apibase, password, **msg):
    """ Process an uploaded scan.
    """
    url = msg['url']

    print 'Decoding scan', msg['scan_id']
    decode.main(apibase, password, msg['scan_id'], url)


@celery.task
def composePrint(apibase, password, **msg):
    """ Create an atlas.
    """
    kwargs = dict(print_id=msg['print_id'],
                  paper_size=msg['paper_size'],
                  orientation=msg['orientation'],
                  layout=msg.get('layout', 'full-page'),
                  pages=msg['pages'])
    
    if 'form_id' in msg and 'form_url' in msg:
        def on_fields(fields):
            for page in msg['pages']:
                page['text'] = (page.get('text', '').strip() + '\n\n' + forms.fields_as_text(fields['fields'])).strip()
        
        print 'Composing print', msg['print_id'], 'and form', msg['form_id']
        compose.main(apibase, password, **kwargs)
        forms.main(apibase, password, msg['form_id'], msg['form_url'], on_fields)
    
    else:
        if 'form_fields' in msg:
            for page in msg['pages']:
                page['text'] = (page.get('text', '').strip() + '\n\n' + forms.fields_as_text(msg['form_fields'])).strip()
    
        print 'Composing print', msg['print_id']
        compose.main(apibase, password, **kwargs)


@celery.task
def parseForm(apibase, password, **msg):
    """
    """
    print 'Parsing a form.'
    return forms.main(apibase, password, msg['form_id'], msg['url'])
