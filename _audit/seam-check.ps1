$code = @'
using System;
using System.Drawing;
public class SeamCheck {
  public static void Run() {
    string[] files = { "c:\\Users\\asukharev\\GitHub\\DS\\_audit\\_real_dpr1.75_fixed.png", "c:\\Users\\asukharev\\GitHub\\DS\\_audit\\_real_dpr1.75_old.png", "c:\\Users\\asukharev\\GitHub\\DS\\_audit\\_real_dpr2_fixed.png", "c:\\Users\\asukharev\\GitHub\\DS\\_audit\\_real_dpr2_old.png" };
    foreach (string f in files) {
      using (var bmp = new Bitmap(f)) {
        Console.WriteLine("== " + System.IO.Path.GetFileName(f) + " " + bmp.Width + "x" + bmp.Height);
        int bright = 0; int bx = -1; int by = -1; int br = 0;
        for (int y = 8; y < bmp.Height - 8; y++) {
          for (int x = 6; x < Math.Min(88, bmp.Width); x++) {
            Color c = bmp.GetPixel(x, y);
            int mn = Math.Min(c.R, Math.Min(c.G, c.B));
            if (mn > 150) { bright++; if (c.R > br) { br = c.R; bx = x; by = y; } }
          }
        }
        Console.WriteLine("bright(min>150) x6..88: " + bright + (bright > 0 ? ("  brightestR=" + br + " at " + bx + "," + by) : ""));
        int mid = bmp.Height / 2;
        Console.Write("row60  R: ");
        for (int x = 6; x <= 60; x++) { Color c = bmp.GetPixel(x, 60); Console.Write(c.R + " "); }
        Console.WriteLine();
        Console.Write("row" + mid + " R: ");
        for (int x = 6; x <= 60; x++) { Color c = bmp.GetPixel(x, mid); Console.Write(c.R + " "); }
        Console.WriteLine();
      }
    }
  }
}
'@
Add-Type -TypeDefinition $code -ReferencedAssemblies System.Drawing
[SeamCheck]::Run()
