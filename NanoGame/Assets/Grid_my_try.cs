using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Grid_my_try : MonoBehaviour
{

    private Vector3[] vertices;
    public int xSize;
    public int ySize;
    private Mesh mesh;
    private void Generate(){
        
        GetComponent<MeshFilter>().mesh = mesh = new Mesh();
        mesh.name = "My Mesh";


        vertices = new Vector3[(xSize+1)*(ySize+1)];
        for (int i=0,x=0;x<=xSize;x++){
            for (int y=0;y<=ySize;y++,i++){
                vertices[i] =  new Vector3(x,y);
                Debug.Log(vertices[i].ToString());
            }
        }
        mesh.vertices = vertices;


        int[] triangles = new int[6];
        triangles[0] = 0;
        triangles[1] = 1;
        triangles[2] = 2;

        triangles[3] = 3;
        triangles[4] = 2;
        triangles[5] = 1;
        mesh.triangles = triangles;

        
        
        
        //mesh.triangles = new int[] {0,1,2};
        
        







        // int[] triangles = new int[xSize * ySize * 6];
        // for (int ti=0,vi=0,y=0; y<ySize;y++,vi++){
        //     triangles[ti] = 
        // }

    }

    private void OnDrawGizmos(){
        if (vertices == null){
            return;
        }
        Gizmos.color = Color.black;
        for (int i =0; i<vertices.Length;i++){
            Gizmos.DrawSphere(vertices[i],0.1f);
        }
    }

    void Start(){
        Generate();
    }


}
