#include <iostream>
#include <fstream>
#include <vector>
#include <windows.h>
#include <GL/gl.h>
#include <ctime>

#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"

using namespace std;

ofstream fout;
vector < vector < pair < short, short > > > framedata;
int realx = 1920;
int realy = 1080;
int winmx = realx/2 + 16;
int winmy = realy/2 + 39;
int winpx = winmx;
int winpy = winmy;
int wx = realx/2;
int wy = realy/2;
float fs = float (wx) / realx;
int cx = 0;
int cy = 0;
float scale = 1.0;
int stepx = 128;
int stepy = 128;
unsigned int textid = 0;
bool showdots = true;
bool showlines = true;
struct color {float r, g, b;} dotcol {0.9, 0.5, 0.1}, linecol {0.2, 0.5, 0.8};

bool loadtx ()
{
    SetForegroundWindow (GetConsoleWindow ());
    framedata.clear ();
    framedata.push_back (vector < pair < short, short > > (0));
    int fid;
    cout << "Enter file id (or -1 if you want to end): ";
    cin >> fid;
    if (fid == -1)
    {
        fout.seekp (int (fout.tellp ()) - 1);
        fout << endl;
        return false;
    }

    char ttd [3];
    itoa (fid, ttd, 10);
    string fname (ttd);
    fname = "img" + fname + ".jpg";

    ifstream ffs ("data/" + fname, ios::ate | ios::binary);
    int fsize = ffs.tellg ();
    ffs.close ();

    fout << endl;
    //fout << "\t\"" << fname << fsize << "\": {" << endl;
    fout << "\t\"" << ttd << "\": {" << endl;
    fout << "\t\t\"fileref\": \"\"," << endl;
    fout << "\t\t\"size\": " << fsize << "," << endl;
    fout << "\t\t\"filename\": \"" << fname << "\"," << endl;
    fout << "\t\t\"base64_img_data\": \"\"," << endl;
    fout << "\t\t\"file_attributes\": {}," << endl;
    fout << "\t\t\"regions\": {" << endl;

    int width, height, comnt;
    unsigned char* data = stbi_load (("data/" + fname).c_str (), &width, &height, &comnt, 0);
    glGenTextures (1, &textid);
    glBindTexture (GL_TEXTURE_2D, textid);
        glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP);
        glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP);
        glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri (GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        //glTexImage2D (GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_BGR_EXT, GL_UNSIGNED_BYTE, data);
        glTexImage2D (GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, data);
    glBindTexture (GL_TEXTURE_2D, 0);
    stbi_image_free (data);
    return true;
}

LRESULT CALLBACK wcb (HWND hwnd, UINT umsg, WPARAM wparam, LPARAM lparam)
{
    switch (umsg)
    {
        case WM_CLOSE:
            PostQuitMessage (0);
            break;
        case WM_DESTROY:
            return 0;
        case WM_LBUTTONDOWN:
        {
            int x = LOWORD (lparam) / fs / scale + cx;
            int y = HIWORD (lparam) / fs / scale + cy;
            cout << "Dot " << x << ' ' << y << " added to group " << framedata.size () - 1 << endl;
            if (!framedata.empty ()) {framedata.back ().push_back ({x, y});}
        }
            break;
        case WM_KEYDOWN:
        {
            switch (wparam)
            {
                case VK_HOME:
                    cout << endl;
                    if (!framedata.empty ()) {framedata.pop_back ();}
                    for (unsigned int i = 0; i < framedata.size (); i ++)
                    {
                        fout << "\t\t\t\"" << i << "\": {" << endl;
                        fout << "\t\t\t\t\"shape_attributes\": {" << endl;
                        fout << "\t\t\t\t\t\"name\": \"polygon\"," << endl;
                        fout << "\t\t\t\t\t\"all_points_x\": [";
                        for (unsigned int j = 0; j < framedata [i].size (); j ++)
                        {
                            fout << framedata [i] [j].first << ", ";
                        }
                        fout << framedata [i] [0].first << "]," << endl;
                        fout << "\t\t\t\t\t\"all_points_y\": [";
                        for (unsigned int j = 0; j < framedata [i].size (); j ++)
                        {
                            fout << framedata [i] [j].second << ", ";
                        }
                        fout << framedata [i] [0].second << "]" << endl;
                        fout << "\t\t\t\t}," << endl;
                        fout << "\t\t\t\t\"region_attributes\": {}" << endl;
                        fout << "\t\t\t}";
                        if (i != framedata.size () - 1) {fout << ',';}
                        fout << endl;
                    }
                    fout << "\t\t}" << endl;
                    fout << "\t},";

                    if (!loadtx ()) {PostQuitMessage (0);}
                    else {SetForegroundWindow (hwnd);}
                    break;
                case 13:
                    if (!framedata.back ().empty ())
                    {
                        cout << "Group " << framedata.size () - 1 << " added" << endl << endl;
                        framedata.push_back (vector < pair < short, short > > (0));
                    }
                    break;
                case VK_DELETE:
                    if (framedata.size () > 1)
                    {
                        cout << "Group " << framedata.size () - 1 << " deleted" << endl << endl;
                        framedata.pop_back ();
                    }
                    break;
                case VK_BACK:
                    if (!framedata.empty () && !framedata.back ().empty ())
                    {
                        cout << "Dot " << framedata.back ().back ().first << ' ' << framedata.back (). back ().second << " removed from group " << framedata.size () - 1 << endl;
                        framedata.back ().pop_back ();
                    }
                    break;
                case 189:
                    scale = max (float (1), scale / 2);
                    cx = min (cx, int (realx - realx / scale));
                    cy = min (cy, int (realy - realy / scale));
                    break;
                case 187:
                    scale = min (float (64), scale * 2);
                    break;
                case VK_UP:
                    cy = max (cy - stepy / scale, 0.0f);
                    break;
                case VK_DOWN:
                    cy = min (cy + stepy / scale, realy - realy / scale);
                    break;
                case VK_LEFT:
                    cx = max (cx - stepx / scale, 0.0f);
                    break;
                case VK_RIGHT:
                    cx = min (cx + stepx / scale, realx - realx / scale);
                    break;
                case 'D':
                    showdots = !showdots;
                    break;
                case 'L':
                    showlines = !showlines;
                    break;
                case 'Y':
                    dotcol.r = (rand () % 1024) / 1024.0;
                    dotcol.g = (rand () % 1024) / 1024.0;
                    dotcol.b = (rand () % 1024) / 1024.0;
                    break;
                case 'T':
                    linecol.r = (rand () % 1024) / 1024.0;
                    linecol.g = (rand () % 1024) / 1024.0;
                    linecol.b = (rand () % 1024) / 1024.0;
                    break;
            }
        }
            break;
        case WM_GETMINMAXINFO:
        {
            LPMINMAXINFO mmi = (LPMINMAXINFO) lparam;
            mmi -> ptMinTrackSize.x = winmx;
            mmi -> ptMinTrackSize.y = winmy;
            mmi -> ptMaxTrackSize.x = winpx*2;
            mmi -> ptMaxTrackSize.y = winpy*2;
        }
            break;
        case WM_SIZE:
            wx = LOWORD (lparam);
            wy = HIWORD (lparam);
            fs = float (wx) / realx;
            glViewport (0, 0, wx, wy);
            break;
        case WM_EXITSIZEMOVE:
            {
                int twy = round (wx * 0.5625);
                if (twy != wy)
                {
                    SetWindowPos (hwnd, 0, 0, 0, wx + 16, twy + 39, SWP_NOMOVE | SWP_NOREPOSITION | SWP_NOOWNERZORDER);
                }
            }
            break;
        default:
            return DefWindowProc (hwnd, umsg, wparam, lparam);
    }
    return 0;
}

int main ()
{
    srand (time (0));
    string jsf;
    cout << "Enter JSON file name: ";
    cin >> jsf;
    fout.open (jsf);
    fout << '{';

    WNDCLASSEX wcgc;
    ZeroMemory (&wcgc, sizeof (wcgc));
    wcgc.lpszClassName = "gc";
    wcgc.cbSize = sizeof (WNDCLASSEX);
    wcgc.style = CS_OWNDC;
    wcgc.lpfnWndProc = wcb;
    if (!RegisterClassEx (&wcgc)) {return 1;}

    RECT desktop;
    const HWND hwnd_desktop = GetDesktopWindow ();
    GetWindowRect (hwnd_desktop, &desktop);
    winpx = desktop.right;
    winpy = desktop.bottom;

    HWND hwnd = CreateWindowEx (0, "gc", "Dotter", WS_SYSMENU | WS_SIZEBOX, winpx/2 - winmx/2, winpy/2 - winmy/2, winmx, winmy, 0, 0, 0, 0);
    //RECT rect;
    //GetWindowRect (hwnd, &rect);
    //cout << rect.right - rect.left << ' ' << rect.bottom - rect.top << endl;
    //GetClientRect (hwnd, &rect);
    //cout << rect.right - rect.left << ' ' << rect.bottom - rect.top << endl;

    HDC hdc = GetDC (hwnd);
    PIXELFORMATDESCRIPTOR pfd;
    ZeroMemory (&pfd, sizeof (pfd));

    pfd.nSize = sizeof (pfd);
    pfd.nVersion = 1;
    pfd.dwFlags = PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER;
    pfd.iPixelType = PFD_TYPE_RGBA;
    pfd.cColorBits = 24;
    pfd.cDepthBits = 16;
    pfd.iLayerType = PFD_MAIN_PLANE;

    int iFormat = ChoosePixelFormat (hdc, &pfd);
    SetPixelFormat (hdc, iFormat, &pfd);
    HGLRC hrc = wglCreateContext (hdc);
    wglMakeCurrent (hdc, hrc);

    loadtx ();
    ShowWindow (hwnd, SW_SHOW);
    SetForegroundWindow (hwnd);
    MSG msg;
    const float vertex [] = {-1, -1,    1, -1,    1, 1,    -1, 1};
    const float tcord [] = {0, 1,    1, 1,    1, 0,    0, 0};
    while (true)
    {
        if (PeekMessage (&msg, NULL, 0, 0, PM_REMOVE))
        {
            if (msg.message == WM_QUIT) {break;}
            else
            {
                TranslateMessage (&msg);
                DispatchMessage (&msg);
            }
        }
        else
        {
            glClearColor (0.0f, 0.0f, 0.0f, 0.0f);
            glClear (GL_COLOR_BUFFER_BIT);

            glColor3f (1, 1, 1);
            glPushMatrix ();

            glEnable (GL_TEXTURE_2D);
            glBindTexture (GL_TEXTURE_2D, textid);
                glTranslatef (-2*scale*cx/realx + scale - 1, 2*scale*cy/realy - scale + 1, 0);
                glScalef (scale, scale, 1);

                glEnableClientState (GL_VERTEX_ARRAY);
                glEnableClientState (GL_TEXTURE_COORD_ARRAY);

                glVertexPointer (2, GL_FLOAT, 0, vertex);
                glTexCoordPointer (2, GL_FLOAT, 0, tcord);
                glDrawArrays (GL_TRIANGLE_FAN, 0, 4);

                glDisableClientState (GL_VERTEX_ARRAY);
                glDisableClientState (GL_TEXTURE_COORD_ARRAY);
            glBindTexture (GL_TEXTURE_2D, 0);
            glDisable (GL_TEXTURE_2D);

            if (showlines)
            {
                glLineWidth (2);
                glColor3f (linecol.r, linecol.g, linecol.b);
                for (auto i : framedata)
                {
                    glBegin (GL_LINE_STRIP);
                    for (auto p : i)
                    {
                        glVertex2f (2.0 * p.first / realx - 1, 1 - 2.0 * p.second / realy);
                    }
                    if (!i.empty ()) {glVertex2f (2.0 * i [0].first / realx - 1, 1 - 2.0 * i [0].second / realy);}
                    glEnd ();
                }
            }

            if (showdots)
            {
                glPointSize (4);
                glColor3f (dotcol.r, dotcol.g, dotcol.b);
                glBegin (GL_POINTS);
                    for (auto i : framedata)
                    {
                        for (auto p : i)
                        {
                            glVertex2f (2.0 * p.first / realx - 1, 1 - 2.0 * p.second / realy);
                        }
                    }
                glEnd ();
            }

            glPopMatrix ();

            SwapBuffers (hdc);
        }
    }

    glDeleteTextures (1, &textid);
    wglMakeCurrent (NULL, NULL);
    wglDeleteContext (hrc);
    ReleaseDC (hwnd, hdc);
    DestroyWindow (hwnd);

    fout << '}' << endl;
    fout.close ();
    return 0;
}
