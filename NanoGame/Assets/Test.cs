using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Test : MonoBehaviour
{
    // Start is called before the first frame update
    public RectTransform selectorImage;
    Rect selectionRect;

    Vector2 startPos;
    Vector2 endPos;

    void Update(){
        if(Input.GetMouseButtonDown(0)){// left mousekey
            //DESELECT ALL
            startPos = Input.mousePosition;
            selectionRect = new Rect();
        }
        if (Input.GetMouseButton(0)) {//While holding down
            endPos = Input.mousePosition;
            DrawRectangle();
        }

        if (Input.GetMouseButtonUp(0)){
            startPos = endPos = Vector2.zero;
            DrawRectangle();
        }
    }

void DrawRectangle(){
    Vector2 boxStart = startPos;
    Vector2 center = (boxStart + endPos)/2;

    selectorImage.position = center;

    float sizeX = Mathf.Abs(boxStart.x - endPos.x);
    float sizeY = Mathf.Abs(boxStart.y - endPos.y);

    selectorImage.sizeDelta = new Vector2(sizeX,sizeY);
    
}

}
