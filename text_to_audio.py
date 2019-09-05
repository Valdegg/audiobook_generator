
import os
import requests
import re
from xml.etree import ElementTree



def get_token():
    """
    For Microsoft's text to speech service.
    :return:
    """
    subscription_key = '16985d62e6cc443b899e6dd89b9b8a7a'
    fetch_token_url = 'https://westeurope.api.cognitive.microsoft.com/sts/v1.0/issueToken'
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key
    }
    response = requests.post(fetch_token_url, headers=headers)
    return str(response.text)


def save_audio(tts, filename, gender = 'female'):
    '''
     The text in 'tts' has been read aloud into filename.wav.

    :param tts: a string to be read aloud by
    :param filename: is the path to the audiofile which will be created
    :param gender: 'male'/'female'
    :return:   1 if it worked, 0 otherwise
    '''

    base_url = 'https://westeurope.tts.speech.microsoft.com/'
    path = 'cognitiveservices/v1'
    constructed_url = base_url + path
    headers = {
        'Authorization': 'Bearer ' + get_token(),
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
        'User-Agent': 'TTS-test'
    }
    xml_body = ElementTree.Element('speak', version='1.0')
    xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-us')
    voice = ElementTree.SubElement(xml_body, 'voice')

    voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-US')
    voice_name = 'JessaNeural' if gender == 'female' else 'GuyNeural'
    voice.set('name', 'Microsoft Server Speech Text to Speech Voice (en-US, ' + voice_name + ')')

    voice.text = tts
    body = ElementTree.tostring(xml_body)

    response = requests.post(constructed_url, headers=headers, data=body)
    if response.status_code == 200:
        with open(filename + '.wav', 'wb') as audio:
            audio.write(response.content)
        return 1
    return 0


def find_chapter(book, chapter_name):
    """
    skilar hvar í bókarstrengnum kaflinn byrjar
    """
    first_occurence = book.find(chapter_name)
    # efinisyfirlitið

    return first_occurence + book[first_occurence + 10:].find(chapter_name)




def collect_chapters(book, table_of_contents):
    """

    :param table_of_contents:
    :return: list of chapters with names in the table of contents
    """
    kaflar = []
    for i in range(len(table_of_contents)-1):

        kaflar.append(book[ find_chapter(book, table_of_contents[i]) :  find_chapter(book, table_of_contents[i+1])])
    return kaflar


def split_chapter(kafli, n_letters):
    """

    Gæti vantað aftasta orðið í aftasta

    :param kafli: chapter to be read aloud
    :param n_letters: number of letters to be read per audio file
    :return:
    """
    text_pieces = []

    while kafli:
        text_pieces.append(kafli[:n_letters].rsplit(' ', 1)[0])
        extraletters = len(kafli[:n_letters].rsplit(' ', 1)[1])
        # extraletters eru auka stafir sem mynda ekki heilt orð, í lok textabrotsins

        kafli = kafli[(n_letters - extraletters):]
        # eyðum því sem búið er að færa inn í text_piece

    return text_pieces



def create_audio(chapter,number, out_path):
    """
    :param chapter: chapter to be read aloud into path
    :param number: chapter number
    :param out_path: destination folder for audio files
    :return:
    """
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    text_pieces = split_chapter(chapter, 5000)

    for i in range(len(text_pieces)):
        file_path = os.path.join(out_path, "kafli" + str(number) + "_" + str(i))

        audio_success = save_audio(text_pieces[i],file_path , "female")

        # ef það feilar:

        n_retries = 0
        max_retries = 10
        while (not audio_success and n_retries < max_retries):
            # try again because sometimes it fails
            audio_success = save_audio(text_pieces[i], "kafli" + str(number) + "_" + str(i), "female")
            time.sleep(3)
            n_retries += 1

        if (n_retries == max_retries):
            raise Exception(str(
                max_retries) + ' consecutive failed attempts to access the TTS service! \n Try again later or check subscription. ')



# The input for this program is the name of a text file containing the book to be read aloud,
#  the path to the folder the text file is in,
#  the path to a subdirectory to save the audio in
#  and the table of contents of the book (list of chapter names).


book_name = "Faust's Metropolis.txt"
table_of_contents = [re.sub("^.*: ", "", x) for x in ["III: The Emerging Giant", "IV: From Revolution to Realpolitik", "V: The Rise of Red Berlin", "VI: Imperial Berlin"]]

path = "/Users/valdimareggertsson/Documents/Valdi/History of Berlin"
with open(os.path.join(path, bookname) as f:
    book = f.read()


kaflar = collect_chapters(book, table_of_contents)


# Dæmi:

chapter_folder = os.path.join(path,"kafli4")
create_audio(kaflar[1], 4, chapter_folder)