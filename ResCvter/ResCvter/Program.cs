using System;
using System.Collections;
using System.Resources;
using System.IO;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.Xml;
using Formatting = Newtonsoft.Json.Formatting;

class Program
{
    static void Main()
    {
        using (ResourceReader reader = new ResourceReader("Sdl.LanguagePlatform.NLP.resources"))
        {
            var dict = new Dictionary<string, object>();
            foreach (DictionaryEntry entry in reader)
            {
                dict[entry.Key.ToString()] = entry.Value;
            }

            File.WriteAllText("Sdl.LanguagePlatform.NLP.json", JsonConvert.SerializeObject(dict, Formatting.Indented));
        }
    }
}
