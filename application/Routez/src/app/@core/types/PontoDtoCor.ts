import { PontoDTO } from "../../../api";
import { ColorCSS } from "../enum/Colorcss.enum";

export type PontoDtoCor = PontoDTO & {
    cor: ColorCSS
}